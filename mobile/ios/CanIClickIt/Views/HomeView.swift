import SwiftUI

struct HomeView: View {
    @AppStorage("grandmaModeEnabled") private var grandmaModeEnabled = false
    @State private var showScan = false
    @State private var showQRScanner = false
    @State private var showRecovery = false
    @State private var showHistory = false
    @State private var showSettings = false

    var body: some View {
        if grandmaModeEnabled {
            GrandmaModeView()
        } else {
            standardHome
        }
    }

    private var standardHome: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: Spacing.lg) {
                    headerSection

                    actionCard(
                        icon: "doc.text.magnifyingglass",
                        title: "Check Something",
                        subtitle: "Paste a message, link, or email to check if it's safe",
                        color: .severityInfo
                    ) {
                        showScan = true
                    }

                    actionCard(
                        icon: "camera.viewfinder",
                        title: "Scan QR / Screenshot",
                        subtitle: "Use your camera to scan a QR code or take a screenshot",
                        color: .severityMedium
                    ) {
                        showQRScanner = true
                    }

                    emergencyCard

                    Spacer(minLength: Spacing.xl)
                }
                .padding(.horizontal, Spacing.md)
            }
            .background(Color.neutral50.ignoresSafeArea())
            .navigationTitle("")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button { showHistory = true } label: {
                        Image(systemName: "clock.arrow.circlepath")
                            .foregroundColor(.neutral700)
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button { showSettings = true } label: {
                        Image(systemName: "gearshape")
                            .foregroundColor(.neutral700)
                    }
                }
            }
            .sheet(isPresented: $showScan) { NavigationStack { ScanView() } }
            .sheet(isPresented: $showQRScanner) { NavigationStack { QRScannerView() } }
            .sheet(isPresented: $showRecovery) { NavigationStack { RecoveryView() } }
            .sheet(isPresented: $showHistory) { NavigationStack { ScanHistoryView() } }
            .sheet(isPresented: $showSettings) { NavigationStack { SettingsView() } }
        }
    }

    // MARK: - Header

    private var headerSection: some View {
        VStack(spacing: Spacing.sm) {
            Image(systemName: "shield.checkered")
                .font(.system(size: 48))
                .foregroundColor(.severityInfo)
                .padding(.top, Spacing.lg)

            Text("Can I Click It?")
                .font(AppFont.h1())
                .foregroundColor(.neutral900)

            Text("Your personal safety assistant")
                .font(AppFont.body())
                .foregroundColor(.neutral500)
        }
        .padding(.bottom, Spacing.sm)
    }

    // MARK: - Action Card

    private func actionCard(
        icon: String,
        title: String,
        subtitle: String,
        color: Color,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.md) {
                ZStack {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(color.opacity(0.12))
                        .frame(width: 48, height: 48)
                    Image(systemName: icon)
                        .font(.system(size: 22))
                        .foregroundColor(color)
                }

                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(title)
                        .font(AppFont.h2())
                        .foregroundColor(.neutral900)
                    Text(subtitle)
                        .font(AppFont.bodySmall())
                        .foregroundColor(.neutral500)
                        .multilineTextAlignment(.leading)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.neutral400)
            }
            .cardStyle()
        }
        .buttonStyle(.plain)
    }

    // MARK: - Emergency Card

    private var emergencyCard: some View {
        Button { showRecovery = true } label: {
            HStack(spacing: Spacing.md) {
                ZStack {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.severityCritical.opacity(0.12))
                        .frame(width: 48, height: 48)
                    Image(systemName: "exclamationmark.shield")
                        .font(.system(size: 22))
                        .foregroundColor(.severityCritical)
                }

                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text("I Already Clicked It")
                        .font(AppFont.h2())
                        .foregroundColor(.severityCritical)
                    Text("Don't worry — let's fix this together.")
                        .font(AppFont.bodySmall())
                        .foregroundColor(.neutral500)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.neutral400)
            }
            .padding(Spacing.lg)
            .background(Color.severityCritical.opacity(0.04))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.severityCritical.opacity(0.2), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    HomeView()
}
