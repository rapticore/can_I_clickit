import SwiftUI

struct SettingsView: View {
    @Environment(\.dismiss) private var dismiss
    @AppStorage("grandmaModeEnabled") private var grandmaModeEnabled = false
    @AppStorage("preferredLanguage") private var preferredLanguage = "en"

    private let languages = [
        ("en", "English"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("zh", "Chinese"),
        ("hi", "Hindi"),
        ("ar", "Arabic"),
    ]

    var body: some View {
        List {
            accessibilitySection
            languageSection
            aboutSection
        }
        .navigationTitle("Settings")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Close") { dismiss() }
            }
        }
    }

    // MARK: - Accessibility

    private var accessibilitySection: some View {
        Section {
            Toggle(isOn: $grandmaModeEnabled) {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text("Simple Mode")
                        .font(AppFont.body())
                        .foregroundColor(.neutral900)

                    Text("Larger text, bigger buttons, voice-first experience. Perfect for anyone who wants a simpler interface.")
                        .font(AppFont.caption())
                        .foregroundColor(.neutral500)
                }
            }
            .tint(.severityInfo)
        } header: {
            Text("Accessibility")
        }
    }

    // MARK: - Language

    private var languageSection: some View {
        Section {
            Picker("Language", selection: $preferredLanguage) {
                ForEach(languages, id: \.0) { code, name in
                    Text(name).tag(code)
                }
            }
            .font(AppFont.body())
        } header: {
            Text("Language")
        } footer: {
            Text("Verdicts and recovery guidance will be provided in your selected language when available.")
                .font(AppFont.caption())
        }
    }

    // MARK: - About

    private var aboutSection: some View {
        Section {
            HStack {
                Text("Version")
                    .font(AppFont.body())
                Spacer()
                Text("1.0.0")
                    .font(AppFont.bodySmall())
                    .foregroundColor(.neutral500)
            }

            Link(destination: URL(string: "https://caniclickit.com/privacy")!) {
                HStack {
                    Text("Privacy Policy")
                        .font(AppFont.body())
                        .foregroundColor(.neutral900)
                    Spacer()
                    Image(systemName: "arrow.up.right.square")
                        .foregroundColor(.neutral400)
                }
            }

            Link(destination: URL(string: "https://caniclickit.com/terms")!) {
                HStack {
                    Text("Terms of Service")
                        .font(AppFont.body())
                        .foregroundColor(.neutral900)
                    Spacer()
                    Image(systemName: "arrow.up.right.square")
                        .foregroundColor(.neutral400)
                }
            }
        } header: {
            Text("About")
        }
    }
}

#Preview {
    NavigationStack {
        SettingsView()
    }
}
