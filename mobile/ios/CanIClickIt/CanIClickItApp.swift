import SwiftUI

@main
struct CanIClickItApp: App {
    @AppStorage("grandmaModeEnabled") private var grandmaModeEnabled = false

    var body: some Scene {
        WindowGroup {
            HomeView()
                .onOpenURL { url in
                    handleIncomingURL(url)
                }
        }
    }

    private func handleIncomingURL(_ url: URL) {
        // Deep link handling for share extension: caniclickit://scan?content=...
        guard url.scheme == "caniclickit",
              url.host == "scan",
              let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let _ = components.queryItems?.first(where: { $0.name == "content" })?.value else {
            return
        }
    }
}
