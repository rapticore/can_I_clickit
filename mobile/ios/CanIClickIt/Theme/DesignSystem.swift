import SwiftUI

// MARK: - Color Tokens

extension Color {
    // Neutral Palette
    static let neutral0   = Color(hex: "FFFFFF")
    static let neutral50  = Color(hex: "F9FAFB")
    static let neutral100 = Color(hex: "F2F4F7")
    static let neutral200 = Color(hex: "EAECF0")
    static let neutral300 = Color(hex: "D0D5DD")
    static let neutral400 = Color(hex: "98A2B3")
    static let neutral500 = Color(hex: "667085")
    static let neutral600 = Color(hex: "475467")
    static let neutral700 = Color(hex: "344054")
    static let neutral800 = Color(hex: "1D2939")
    static let neutral900 = Color(hex: "101828")

    // Severity Colors
    static let severityCritical = Color(hex: "D92D20")
    static let severityHigh     = Color(hex: "F04438")
    static let severityMedium   = Color(hex: "F79009")
    static let severitySafe     = Color(hex: "12B76A")
    static let severityInfo     = Color(hex: "2E90FA")

    init(hex: String) {
        let scanner = Scanner(string: hex.trimmingCharacters(in: CharacterSet(charactersIn: "#")))
        var rgb: UInt64 = 0
        scanner.scanHexInt64(&rgb)
        self.init(
            red: Double((rgb >> 16) & 0xFF) / 255.0,
            green: Double((rgb >> 8) & 0xFF) / 255.0,
            blue: Double(rgb & 0xFF) / 255.0
        )
    }
}

// MARK: - Typography

struct AppFont {
    static let familyName = "Inter"

    static func h1() -> Font {
        .custom(familyName, size: 30).weight(.bold)
    }

    static func h2() -> Font {
        .custom(familyName, size: 22).weight(.semibold)
    }

    static func body() -> Font {
        .custom(familyName, size: 16).weight(.regular)
    }

    static func bodySmall() -> Font {
        .custom(familyName, size: 14).weight(.regular)
    }

    static func caption() -> Font {
        .custom(familyName, size: 12).weight(.regular)
    }

    static func grandmaBody() -> Font {
        .custom(familyName, size: 24).weight(.medium)
    }

    static func grandmaButton() -> Font {
        .custom(familyName, size: 28).weight(.bold)
    }
}

// MARK: - Spacing

struct Spacing {
    static let xs:  CGFloat = 4
    static let sm:  CGFloat = 8
    static let md:  CGFloat = 16
    static let lg:  CGFloat = 24
    static let xl:  CGFloat = 32
    static let xxl: CGFloat = 48
}

// MARK: - Card Style

struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(Spacing.lg)
            .background(Color.neutral0)
            .cornerRadius(8)
            .shadow(color: .black.opacity(0.06), radius: 4, x: 0, y: 2)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardStyle())
    }
}

// MARK: - Primary Button Style

struct PrimaryButtonStyle: ButtonStyle {
    var backgroundColor: Color = .severityInfo

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(AppFont.body())
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.lg)
            .padding(.vertical, Spacing.md)
            .background(backgroundColor)
            .cornerRadius(8)
            .opacity(configuration.isPressed ? 0.85 : 1.0)
    }
}

// MARK: - Danger Button Style

struct DangerButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(AppFont.body())
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.lg)
            .padding(.vertical, Spacing.md)
            .background(Color.severityCritical)
            .cornerRadius(8)
            .opacity(configuration.isPressed ? 0.85 : 1.0)
    }
}
