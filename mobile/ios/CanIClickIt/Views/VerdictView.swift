import SwiftUI

struct VerdictView: View {
    @Environment(\.dismiss) private var dismiss
    @StateObject private var speechService = SpeechService()

    let result: ScanResult
    let inputPreview: String

    @State private var feedbackGiven = false
    @State private var feedbackAccurate: Bool?

    private var headerColor: Color {
        switch result.threatLevel {
        case .safe:       return .severitySafe
        case .suspicious: return .severityMedium
        case .dangerous:  return .severityCritical
        }
    }

    private var headerIcon: String {
        switch result.threatLevel {
        case .safe:       return "checkmark.shield.fill"
        case .suspicious: return "exclamationmark.triangle.fill"
        case .dangerous:  return "xmark.shield.fill"
        }
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                verdictHeader
                verdictBody
            }
        }
        .background(Color.neutral50.ignoresSafeArea())
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Done") { dismiss() }
            }
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    speechService.speak(result.verdict)
                } label: {
                    Image(systemName: speechService.isSpeaking ? "speaker.wave.3.fill" : "speaker.wave.2")
                }
            }
        }
    }

    // MARK: - Header

    private var verdictHeader: some View {
        VStack(spacing: Spacing.md) {
            Image(systemName: headerIcon)
                .font(.system(size: 56))
                .foregroundColor(.white)

            Text(result.threatLevel.displayName.uppercased())
                .font(AppFont.h1())
                .foregroundColor(.white)

            Text(result.verdict)
                .font(AppFont.body())
                .foregroundColor(.white.opacity(0.95))
                .multilineTextAlignment(.center)
                .padding(.horizontal, Spacing.lg)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, Spacing.xl)
        .background(headerColor)
    }

    // MARK: - Body

    private var verdictBody: some View {
        VStack(spacing: Spacing.lg) {
            confidenceMeter
            if let consequences = result.consequences, !consequences.isEmpty {
                consequencesBlock(consequences)
            }
            if let safeAction = result.safeAction, !safeAction.isEmpty {
                safeActionBlock(safeAction)
            }
            signalsSection
            disclaimerText
            feedbackSection
        }
        .padding(Spacing.md)
    }

    // MARK: - Confidence Meter

    private var confidenceMeter: some View {
        VStack(alignment: .leading, spacing: Spacing.sm) {
            HStack {
                Text("Confidence")
                    .font(AppFont.bodySmall())
                    .foregroundColor(.neutral600)
                Spacer()
                Text(result.confidence.displayName)
                    .font(AppFont.bodySmall())
                    .foregroundColor(.neutral700)
            }

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.neutral200)
                        .frame(height: 8)

                    RoundedRectangle(cornerRadius: 4)
                        .fill(headerColor)
                        .frame(width: geo.size.width * result.confidence.fraction, height: 8)
                }
            }
            .frame(height: 8)
        }
        .cardStyle()
    }

    // MARK: - Consequences

    private func consequencesBlock(_ text: String) -> some View {
        HStack(alignment: .top, spacing: Spacing.md) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 20))
                .foregroundColor(.severityMedium)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("Potential Consequences")
                    .font(AppFont.h2())
                    .foregroundColor(.neutral900)
                Text(text)
                    .font(AppFont.body())
                    .foregroundColor(.neutral700)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.lg)
        .background(Color.severityMedium.opacity(0.06))
        .cornerRadius(8)
    }

    // MARK: - Safe Action

    private func safeActionBlock(_ text: String) -> some View {
        HStack(alignment: .top, spacing: Spacing.md) {
            Image(systemName: "hand.thumbsup")
                .font(.system(size: 20))
                .foregroundColor(.severitySafe)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("What You Should Do")
                    .font(AppFont.h2())
                    .foregroundColor(.neutral900)
                Text(text)
                    .font(AppFont.body())
                    .foregroundColor(.neutral700)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.lg)
        .background(Color.severitySafe.opacity(0.06))
        .cornerRadius(8)
    }

    // MARK: - Signals

    private var signalsSection: some View {
        Group {
            if !result.signals.isEmpty {
                VStack(alignment: .leading, spacing: Spacing.sm) {
                    Text("Analysis Signals")
                        .font(AppFont.h2())
                        .foregroundColor(.neutral900)

                    ForEach(result.signals) { signal in
                        HStack {
                            Circle()
                                .fill(headerColor)
                                .frame(width: 6, height: 6)
                            Text(signal.verdict)
                                .font(AppFont.bodySmall())
                                .foregroundColor(.neutral700)
                            Spacer()
                        }
                    }
                }
                .cardStyle()
            }
        }
    }

    // MARK: - Disclaimer

    private var disclaimerText: some View {
        Text("This analysis is our best assessment based on available signals.")
            .font(AppFont.caption())
            .foregroundColor(.neutral400)
            .multilineTextAlignment(.center)
            .padding(.horizontal, Spacing.md)
    }

    // MARK: - Feedback

    private var feedbackSection: some View {
        VStack(spacing: Spacing.sm) {
            Text("Was this verdict correct?")
                .font(AppFont.body())
                .foregroundColor(.neutral700)

            if feedbackGiven {
                Text("Thanks for your feedback!")
                    .font(AppFont.bodySmall())
                    .foregroundColor(.severitySafe)
            } else {
                HStack(spacing: Spacing.lg) {
                    feedbackButton(accurate: true, icon: "hand.thumbsup", label: "Yes")
                    feedbackButton(accurate: false, icon: "hand.thumbsdown", label: "No")
                }
            }
        }
        .padding(.vertical, Spacing.md)
    }

    private func feedbackButton(accurate: Bool, icon: String, label: String) -> some View {
        Button {
            submitFeedback(accurate: accurate)
        } label: {
            VStack(spacing: Spacing.xs) {
                Image(systemName: icon)
                    .font(.system(size: 24))
                Text(label)
                    .font(AppFont.bodySmall())
            }
            .foregroundColor(.neutral600)
            .frame(width: 72, height: 64)
            .background(Color.neutral100)
            .cornerRadius(8)
        }
    }

    private func submitFeedback(accurate: Bool) {
        feedbackAccurate = accurate
        feedbackGiven = true

        let feedback = FeedbackRequest(scanId: result.id, accurate: accurate, comment: nil)
        Task {
            try? await APIClient.shared.submitFeedback(feedback)
        }
    }
}

#Preview {
    NavigationStack {
        VerdictView(
            result: ScanResult(
                id: "preview-1",
                scanType: .url,
                threatLevel: .suspicious,
                confidence: .medium,
                confidenceScore: 68,
                verdictSummary: "This link appears suspicious.",
                explanation: "This link appears to be a phishing attempt impersonating your bank.",
                consequences: "If you click this link and enter your credentials, attackers could access your bank account.",
                safeAction: "Delete this message and do not click the link. If you're concerned about your account, go directly to your bank's website.",
                signals: [
                    SignalResult(source: "heuristic", score: 80, detail: "Domain mimics a known bank"),
                    SignalResult(source: "intent_detection", score: 65, detail: "Urgency language detected")
                ],
                scannedAt: Date()
            ),
            inputPreview: "Your account has been locked. Click here to verify: http://secure-bank-login.xyz"
        )
    }
}
