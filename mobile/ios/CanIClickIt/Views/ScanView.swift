import SwiftUI

struct ScanView: View {
    @Environment(\.dismiss) private var dismiss
    @StateObject private var speechService = SpeechService()
    @State private var inputText = ""
    @State private var scanResult: ScanResult?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showVerdict = false

    var body: some View {
        ScrollView {
            VStack(spacing: Spacing.lg) {
                instructionSection
                inputSection
                microphoneButton
                scanButton
            }
            .padding(.horizontal, Spacing.md)
            .padding(.top, Spacing.md)
        }
        .background(Color.neutral50.ignoresSafeArea())
        .navigationTitle("Check Something")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Close") { dismiss() }
            }
        }
        .sheet(isPresented: $showVerdict) {
            if let result = scanResult {
                NavigationStack {
                    VerdictView(result: result, inputPreview: inputText)
                }
            }
        }
        .alert("Error", isPresented: .constant(errorMessage != nil)) {
            Button("OK") { errorMessage = nil }
        } message: {
            Text(errorMessage ?? "")
        }
        .onAppear {
            speechService.requestAuthorization()
        }
    }

    // MARK: - Instruction

    private var instructionSection: some View {
        VStack(spacing: Spacing.sm) {
            Text("What would you like to check?")
                .font(AppFont.h2())
                .foregroundColor(.neutral900)

            Text("Paste a message, email, or link you received, or use the microphone to describe what happened.")
                .font(AppFont.bodySmall())
                .foregroundColor(.neutral500)
                .multilineTextAlignment(.center)
        }
    }

    // MARK: - Text Input

    private var inputSection: some View {
        VStack(alignment: .leading, spacing: Spacing.sm) {
            TextEditor(text: $inputText)
                .font(AppFont.body())
                .frame(minHeight: 140)
                .padding(Spacing.sm)
                .background(Color.neutral0)
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.neutral300, lineWidth: 1)
                )
                .overlay(alignment: .topLeading) {
                    if inputText.isEmpty {
                        Text("Paste text, URL, or describe what you received...")
                            .font(AppFont.body())
                            .foregroundColor(.neutral400)
                            .padding(.horizontal, Spacing.sm + 4)
                            .padding(.vertical, Spacing.sm + 8)
                            .allowsHitTesting(false)
                    }
                }

            if !speechService.recognizedText.isEmpty {
                Button("Use voice input") {
                    inputText = speechService.recognizedText
                }
                .font(AppFont.bodySmall())
                .foregroundColor(.severityInfo)
            }
        }
    }

    // MARK: - Microphone

    private var microphoneButton: some View {
        Button {
            toggleListening()
        } label: {
            HStack(spacing: Spacing.sm) {
                Image(systemName: speechService.isListening ? "mic.fill" : "mic")
                    .font(.system(size: 20))
                Text(speechService.isListening ? "Listening..." : "Tap to speak")
                    .font(AppFont.body())
            }
            .foregroundColor(speechService.isListening ? .white : .severityInfo)
            .padding(.horizontal, Spacing.lg)
            .padding(.vertical, Spacing.md)
            .background(speechService.isListening ? Color.severityInfo : Color.severityInfo.opacity(0.1))
            .cornerRadius(24)
        }
    }

    // MARK: - Scan Button

    private var scanButton: some View {
        Button {
            Task { await performScan() }
        } label: {
            HStack {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    Image(systemName: "shield.checkered")
                    Text("Check This")
                }
            }
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(PrimaryButtonStyle())
        .disabled(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isLoading)
        .opacity(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? 0.5 : 1.0)
    }

    // MARK: - Actions

    private func toggleListening() {
        if speechService.isListening {
            speechService.stopListening()
        } else {
            do {
                try speechService.startListening()
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }

    private func performScan() async {
        let trimmed = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        isLoading = true
        errorMessage = nil

        let scanType: ScanType = trimmed.hasPrefix("http://") || trimmed.hasPrefix("https://") ? .url : .text
        let request = ScanRequest(content: trimmed, type: scanType)

        do {
            let result = try await APIClient.shared.scan(request)
            scanResult = result
            saveToHistory(input: trimmed, type: scanType, result: result)
            showVerdict = true
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    private func saveToHistory(input: String, type: ScanType, result: ScanResult) {
        var history = ScanHistoryStore.load()
        let entry = ScanHistoryEntry(inputPreview: input, scanType: type, result: result)
        history.insert(entry, at: 0)
        if history.count > 100 { history = Array(history.prefix(100)) }
        ScanHistoryStore.save(history)
    }
}

// MARK: - Local History Persistence

enum ScanHistoryStore {
    private static let key = "scan_history"

    static func load() -> [ScanHistoryEntry] {
        guard let data = UserDefaults.standard.data(forKey: key) else { return [] }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return (try? decoder.decode([ScanHistoryEntry].self, from: data)) ?? []
    }

    static func save(_ entries: [ScanHistoryEntry]) {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        if let data = try? encoder.encode(entries) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }
}

#Preview {
    NavigationStack {
        ScanView()
    }
}
