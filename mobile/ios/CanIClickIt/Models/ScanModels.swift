import Foundation

// MARK: - Scan Type

enum ScanType: String, Codable, CaseIterable {
    case text
    case url
    case screenshot
    case qrCode = "qr_code"

    var displayName: String {
        switch self {
        case .text:       return "Text"
        case .url:        return "Link"
        case .screenshot: return "Screenshot"
        case .qrCode:     return "QR Code"
        }
    }

    var iconName: String {
        switch self {
        case .text:       return "doc.text"
        case .url:        return "link"
        case .screenshot: return "camera.viewfinder"
        case .qrCode:     return "qrcode.viewfinder"
        }
    }
}

// MARK: - Threat Level

enum ThreatLevel: String, Codable, CaseIterable, Comparable {
    case safe
    case suspicious
    case dangerous

    var displayName: String {
        switch self {
        case .safe:       return "Safe"
        case .suspicious: return "Suspicious"
        case .dangerous:  return "Dangerous"
        }
    }

    var emoji: String {
        switch self {
        case .safe:       return "✅"
        case .suspicious: return "⚠️"
        case .dangerous:  return "🚨"
        }
    }

    private var sortOrder: Int {
        switch self {
        case .safe:       return 0
        case .suspicious: return 1
        case .dangerous:  return 2
        }
    }

    static func < (lhs: ThreatLevel, rhs: ThreatLevel) -> Bool {
        lhs.sortOrder < rhs.sortOrder
    }
}

// MARK: - Confidence Level

enum ConfidenceLevel: String, Codable, CaseIterable {
    case high
    case medium
    case low

    var displayName: String {
        switch self {
        case .high:   return "High Confidence"
        case .medium: return "Medium Confidence"
        case .low:    return "Low Confidence"
        }
    }

    var fraction: Double {
        switch self {
        case .high:   return 0.9
        case .medium: return 0.6
        case .low:    return 0.3
        }
    }
}

// MARK: - Scan Request

struct ScanRequest: Codable {
    let content: String
    let type: ScanType
    let locale: String?

    enum CodingKeys: String, CodingKey {
        case content
        case type = "scan_type"
        case locale = "language"
    }

    init(content: String, type: ScanType, locale: String? = Locale.current.language.languageCode?.identifier) {
        self.content = content
        self.type = type
        self.locale = locale
    }
}

// MARK: - Signal Result

struct SignalResult: Codable, Identifiable {
    let source: String
    let score: Double
    let detail: String

    var id: String { "\(source)-\(detail)" }
    var verdict: String { detail }
}

// MARK: - Scan Result

struct ScanResult: Codable, Identifiable {
    let id: String
    let scanType: ScanType
    let threatLevel: ThreatLevel
    let confidence: ConfidenceLevel
    let confidenceScore: Double
    let verdictSummary: String
    let explanation: String
    let consequences: String?
    let safeAction: String?
    let signals: [SignalResult]
    let scannedAt: Date

    enum CodingKeys: String, CodingKey {
        case id = "scan_id"
        case scanType = "scan_type"
        case threatLevel = "threat_level"
        case confidence
        case confidenceScore = "confidence_score"
        case verdictSummary = "verdict_summary"
        case explanation
        case consequences = "consequence_warning"
        case safeAction = "safe_action_suggestion"
        case signals
        case scannedAt = "created_at"
    }

    var verdict: String {
        verdictSummary
    }
}

// MARK: - Scan History Entry (local persistence)

struct ScanHistoryEntry: Codable, Identifiable {
    let id: String
    let inputPreview: String
    let scanType: ScanType
    let result: ScanResult
    let createdAt: Date

    init(inputPreview: String, scanType: ScanType, result: ScanResult) {
        self.id = UUID().uuidString
        self.inputPreview = String(inputPreview.prefix(120))
        self.scanType = scanType
        self.result = result
        self.createdAt = Date()
    }
}

// MARK: - Feedback

struct FeedbackRequest: Codable {
    let scanId: String
    let userVerdict: String
    let comment: String?

    enum CodingKeys: String, CodingKey {
        case scanId = "scan_id"
        case userVerdict = "user_verdict"
        case comment
    }

    init(scanId: String, accurate: Bool, comment: String? = nil) {
        self.scanId = scanId
        self.userVerdict = accurate ? "correct" : "incorrect_false_negative"
        self.comment = comment
    }
}
