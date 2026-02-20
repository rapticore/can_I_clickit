import Foundation
import UIKit

// MARK: - API Client

final class APIClient: ObservableObject {
    static let shared = APIClient()

    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder

    var baseURL: String {
        guard let url = Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as? String, !url.isEmpty else {
            return "https://api.caniclickit.com"
        }
        return url
    }

    var apiKey: String {
        Bundle.main.object(forInfoDictionaryKey: "API_KEY") as? String ?? ""
    }

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)

        self.decoder = JSONDecoder()
        self.decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let value = try container.decode(String.self)

            if let date = APIClient.iso8601WithFractional.date(from: value) {
                return date
            }
            if let date = APIClient.iso8601Basic.date(from: value) {
                return date
            }
            if let date = APIClient.naiveIsoFormatter.date(from: value) {
                return date
            }
            if let date = APIClient.naiveIsoNoFractionFormatter.date(from: value) {
                return date
            }
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Invalid date format: \(value)"
            )
        }

        self.encoder = JSONEncoder()
        self.encoder.dateEncodingStrategy = .iso8601
    }

    private static let iso8601Basic: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        return formatter
    }()

    private static let iso8601WithFractional: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter
    }()

    private static let naiveIsoFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .iso8601)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
        return formatter
    }()

    private static let naiveIsoNoFractionFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .iso8601)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        return formatter
    }()

    // MARK: - Scan Text / URL

    func scan(_ request: ScanRequest) async throws -> ScanResult {
        let url = try buildURL(path: "/v1/scan")
        var urlRequest = try makeRequest(url: url, method: "POST")
        urlRequest.httpBody = try encoder.encode(request)
        return try await execute(urlRequest)
    }

    // MARK: - Scan Screenshot

    func scanScreenshot(_ image: UIImage) async throws -> ScanResult {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            throw APIError.invalidInput("Could not process image")
        }

        let url = try buildURL(path: "/v1/scan/screenshot")
        var urlRequest = try makeRequest(url: url, method: "POST")

        let boundary = UUID().uuidString
        urlRequest.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"screenshot.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"language\"\r\n\r\n".data(using: .utf8)!)
        body.append("en".data(using: .utf8)!)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        urlRequest.httpBody = body

        return try await execute(urlRequest)
    }

    // MARK: - Recovery Triage

    func submitTriage(answers: [TriageAnswer]) async throws -> RecoveryChecklist {
        let url = try buildURL(path: "/v1/recovery/triage")
        var urlRequest = try makeRequest(url: url, method: "POST")
        let payload = TriageAnswersPayload(answers: answers)
        urlRequest.httpBody = try encoder.encode(payload)
        return try await execute(urlRequest)
    }

    // MARK: - Recovery Checklist by Category

    func getChecklist(for category: ThreatCategory) async throws -> RecoveryChecklist {
        let url = try buildURL(path: "/v1/recovery/checklist/\(category.rawValue)")
        let urlRequest = try makeRequest(url: url, method: "GET")
        return try await execute(urlRequest)
    }

    // MARK: - Feedback

    func submitFeedback(_ feedback: FeedbackRequest) async throws {
        let url = try buildURL(path: "/v1/feedback")
        var urlRequest = try makeRequest(url: url, method: "POST")
        urlRequest.httpBody = try encoder.encode(feedback)
        let _: EmptyResponse = try await execute(urlRequest)
    }

    // MARK: - Health Check

    func healthCheck() async throws -> Bool {
        let url = try buildURL(path: "/v1/health")
        let urlRequest = try makeRequest(url: url, method: "GET")
        let response: HealthResponse = try await execute(urlRequest)
        return response.status == "healthy" || response.status == "degraded"
    }

    // MARK: - Private Helpers

    private func buildURL(path: String) throws -> URL {
        guard let url = URL(string: baseURL + path) else {
            throw APIError.invalidURL
        }
        return url
    }

    private func makeRequest(url: URL, method: String) throws -> URLRequest {
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if !apiKey.isEmpty {
            request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        }
        return request
    }

    private func execute<T: Decodable>(_ request: URLRequest) async throws -> T {
        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.unknown
        }

        switch httpResponse.statusCode {
        case 200...299:
            return try decoder.decode(T.self, from: data)
        case 401:
            throw APIError.unauthorized
        case 429:
            throw APIError.rateLimited
        case 400...499:
            let message = (try? decoder.decode(ErrorResponse.self, from: data))?.detail ?? "Request failed"
            throw APIError.clientError(httpResponse.statusCode, message)
        case 500...599:
            throw APIError.serverError(httpResponse.statusCode)
        default:
            throw APIError.unknown
        }
    }
}

// MARK: - API Errors

enum APIError: LocalizedError {
    case invalidURL
    case invalidInput(String)
    case unauthorized
    case rateLimited
    case clientError(Int, String)
    case serverError(Int)
    case unknown

    var errorDescription: String? {
        switch self {
        case .invalidURL:              return "Invalid server address."
        case .invalidInput(let msg):   return msg
        case .unauthorized:            return "Invalid API key. Please check your settings."
        case .rateLimited:             return "Too many requests. Please wait a moment and try again."
        case .clientError(_, let msg): return msg
        case .serverError(let code):   return "Server error (\(code)). Please try again later."
        case .unknown:                 return "Something went wrong. Please try again."
        }
    }
}

// MARK: - Response Helpers

private struct ErrorResponse: Decodable {
    let detail: String
}

private struct TriageAnswersPayload: Encodable {
    let answers: [TriageAnswer]
}

private struct EmptyResponse: Decodable {}

private struct HealthResponse: Decodable {
    let status: String
}
