import SwiftUI

struct GrandmaModeView: View {
    @AppStorage("grandmaModeEnabled") private var grandmaModeEnabled = true
    @StateObject private var speechService = SpeechService()
    @State private var inputText = ""
    @State private var scanResult: ScanResult?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showVerdict = false
    @State private var showSettings = false

    var body: some View {
        NavigationStack {
            ZStack {
                Color.neutral50.ignoresSafeArea()

                if let result = scanResult, showVerdict {
                    grandmaVerdictView(result)
                } else if isLoading {
                    loadingView
                } else {
                    mainInputView
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button { showSettings = true } label: {
                        Image(systemName: "gearshape")
                            .font(.system(size: 20))
                            .foregroundColor(.neutral600)
                    }
                }
            }
            .sheet(isPresented: $showSettings) {
                NavigationStack { SettingsView() }
            }
            .alert("Something went wrong", isPresented: .constant(errorMessage != nil)) {
                Button("Try Again") { errorMessage = nil }
            } message: {
                Text(errorMessage ?? "")
            }
            .onAppear {
                speechService.requestAuthorization()
            }
        }
    }

    // MARK: - Main Input

    private var mainInputView: some View {
        VStack(spacing: Spacing.xl) {
            Spacer()

            Image(systemName: "shield.checkered")
                .font(.system(size: 64))
                .foregroundColor(.severityInfo)

            Text("Can I Click It?")
                .font(.custom("Inter", size: 32).weight(.bold))
                .foregroundColor(.neutral900)

            Text("Paste what you received below, or tap the microphone to tell us about it.")
                .font(AppFont.grandmaBody())
                .foregroundColor(.neutral600)
                .multilineTextAlignment(.center)
                .padding(.horizontal, Spacing.lg)

            TextEditor(text: $inputText)
                .font(AppFont.grandmaBody())
                .frame(height: 120)
                .padding(Spacing.md)
                .background(Color.neutral0)
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.neutral300, lineWidth: 1)
                )
                .overlay(alignment: .topLeading) {
                    if inputText.isEmpty {
                        Text("Paste here...")
                            .font(AppFont.grandmaBody())
                            .foregroundColor(.neutral400)
                            .padding(.horizontal, Spacing.md + 4)
                            .padding(.vertical, Spacing.md + 8)
                            .allowsHitTesting(false)
                    }
                }
                .padding(.horizontal, Spacing.lg)

            // Giant microphone
            Button {
                toggleListening()
            } label: {
                VStack(spacing: Spacing.sm) {
                    Image(systemName: speechService.isListening ? "mic.fill" : "mic.circle.fill")
                        .font(.system(size: 72))
                        .foregroundColor(speechService.isListening ? .severityCritical : .severityInfo)
                        .scaleEffect(speechService.isListening ? 1.1 : 1.0)
                        .animation(.easeInOut(duration: 0.6).repeatForever(autoreverses: true), value: speechService.isListening)

                    Text(speechService.isListening ? "Listening..." : "Tap to Speak")
                        .font(AppFont.grandmaBody())
                        .foregroundColor(.neutral600)
                }
            }

            // Giant check button
            Button {
                Task { await performScan() }
            } label: {
                Text("Check This")
                    .font(.custom("Inter", size: 28).weight(.bold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, Spacing.lg)
                    .background(
                        inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                            ? Color.neutral300
                            : Color.severityInfo
                    )
                    .cornerRadius(12)
            }
            .disabled(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            .padding(.horizontal, Spacing.lg)

            Spacer()
        }
    }

    // MARK: - Loading

    private var loadingView: some View {
        VStack(spacing: Spacing.lg) {
            ProgressView()
                .scaleEffect(2.0)
                .tint(.severityInfo)

            Text("Checking...")
                .font(AppFont.grandmaBody())
                .foregroundColor(.neutral600)
        }
    }

    // MARK: - Grandma Verdict

    private func grandmaVerdictView(_ result: ScanResult) -> some View {
        let color: Color = {
            switch result.threatLevel {
            case .safe:       return .severitySafe
            case .suspicious: return .severityMedium
            case .dangerous:  return .severityCritical
            }
        }()

        let icon: String = {
            switch result.threatLevel {
            case .safe:       return "checkmark.circle.fill"
            case .suspicious: return "exclamationmark.triangle.fill"
            case .dangerous:  return "xmark.circle.fill"
            }
        }()

        return ScrollView {
            VStack(spacing: Spacing.xl) {
                Spacer(minLength: Spacing.xl)

                Image(systemName: icon)
                    .font(.system(size: 100))
                    .foregroundColor(color)

                Text(result.threatLevel.displayName.uppercased())
                    .font(.custom("Inter", size: 36).weight(.bold))
                    .foregroundColor(color)

                Text(result.verdict)
                    .font(AppFont.grandmaBody())
                    .foregroundColor(.neutral800)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, Spacing.lg)

                // Speak button
                Button {
                    speechService.speak(result.verdict)
                } label: {
                    HStack(spacing: Spacing.sm) {
                        Image(systemName: "speaker.wave.2.fill")
                            .font(.system(size: 24))
                        Text("Read Aloud")
                            .font(AppFont.grandmaBody())
                    }
                    .foregroundColor(.severityInfo)
                    .padding(.horizontal, Spacing.lg)
                    .padding(.vertical, Spacing.md)
                    .background(Color.severityInfo.opacity(0.1))
                    .cornerRadius(12)
                }

                Button {
                    withAnimation {
                        scanResult = nil
                        showVerdict = false
                        inputText = ""
                    }
                } label: {
                    Text("Check Something Else")
                        .font(AppFont.grandmaButton())
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.lg)
                        .background(Color.severityInfo)
                        .cornerRadius(12)
                }
                .padding(.horizontal, Spacing.lg)

                Text("This analysis is our best assessment based on available signals.")
                    .font(AppFont.bodySmall())
                    .foregroundColor(.neutral400)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, Spacing.lg)

                Spacer(minLength: Spacing.xl)
            }
        }
    }

    // MARK: - Actions

    private func toggleListening() {
        if speechService.isListening {
            speechService.stopListening()
            if !speechService.recognizedText.isEmpty {
                inputText = speechService.recognizedText
            }
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
            showVerdict = true
            speechService.speak(result.verdict)
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}

#Preview {
    GrandmaModeView()
}
