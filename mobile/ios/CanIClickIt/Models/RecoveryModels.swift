import Foundation

// MARK: - Threat Category

enum ThreatCategory: String, Codable, CaseIterable, Identifiable {
    var id: String { rawValue }

    case credentialTheft = "credential_theft"
    case financialFraud = "financial_fraud"
    case identityTheft = "identity_theft"
    case malwareDownload = "malware_download"
    case giftCardWire = "gift_card_wire"
    case remoteAccess = "remote_access"
    case generalUnknown = "general_unknown"
    case blackmailSextortion = "blackmail_sextortion"
    case ransomwareExtortion = "ransomware_extortion"
    case pigButchering = "pig_butchering"

    var displayName: String {
        switch self {
        case .credentialTheft: return "I entered my password"
        case .financialFraud: return "I shared banking/card info"
        case .identityTheft: return "I shared personal identity info"
        case .malwareDownload: return "I downloaded or installed something"
        case .giftCardWire: return "I sent gift card/wire/crypto payment"
        case .remoteAccess: return "I gave remote access to my device"
        case .generalUnknown: return "I'm not sure what happened"
        case .blackmailSextortion: return "I got a blackmail/sextortion message"
        case .ransomwareExtortion: return "I got a ransomware/extortion message"
        case .pigButchering: return "Someone pushed me to invest money"
        }
    }

    var iconName: String {
        switch self {
        case .credentialTheft: return "key.fill"
        case .financialFraud: return "creditcard.fill"
        case .identityTheft: return "person.text.rectangle.fill"
        case .malwareDownload: return "ladybug.fill"
        case .giftCardWire: return "gift.fill"
        case .remoteAccess: return "desktopcomputer"
        case .generalUnknown: return "questionmark.circle.fill"
        case .blackmailSextortion: return "exclamationmark.triangle.fill"
        case .ransomwareExtortion: return "lock.doc.fill"
        case .pigButchering: return "chart.line.downtrend.xyaxis"
        }
    }
}

// MARK: - Triage Question

struct TriageQuestion: Codable, Identifiable {
    let id: String
    let question: String
    let options: [TriageOption]
}

struct TriageOption: Codable, Identifiable, Hashable {
    let id: String
    let label: String
    let mapsTo: String?

    enum CodingKeys: String, CodingKey {
        case id
        case label
        case mapsTo = "maps_to"
    }
}

// MARK: - Triage Answer

struct TriageAnswer: Codable {
    let questionId: String
    let selectedOptionId: String

    enum CodingKeys: String, CodingKey {
        case questionId = "question_id"
        case selectedOptionId = "selected_option_id"
    }
}

// MARK: - Recovery Checklist

enum UrgencyLevel: String, Codable {
    case critical
    case high
    case medium
}

struct RecoveryChecklist: Codable, Identifiable {
    let category: ThreatCategory
    let urgency: UrgencyLevel
    let title: String
    let openingMessage: String
    let steps: [RecoveryStep]
    let quickDialContacts: [QuickDialContact]
    let disclaimer: String

    enum CodingKeys: String, CodingKey {
        case category
        case urgency
        case title
        case openingMessage = "opening_message"
        case steps
        case quickDialContacts = "quick_dial_contacts"
        case disclaimer
    }

    var id: String { category.rawValue }
}

// MARK: - Recovery Step

enum StepUrgency: String, Codable {
    case immediate
    case soon
    case later

    var displayName: String {
        switch self {
        case .immediate: return "Do this now"
        case .soon: return "Do this today"
        case .later: return "Do this when you can"
        }
    }
}

struct RecoveryStep: Codable, Identifiable {
    let stepNumber: Int
    let title: String
    let description: String
    let helpDetail: String
    let actionType: String
    let actionData: [String: String]?

    enum CodingKeys: String, CodingKey {
        case stepNumber = "step_number"
        case title
        case description
        case helpDetail = "help_detail"
        case actionType = "action_type"
        case actionData = "action_data"
    }

    var id: String { "step-\(stepNumber)" }
    var order: Int { stepNumber }
    var plainLanguage: String { helpDetail.isEmpty ? description : helpDetail }
    var isCompleted: Bool { false }
    var externalLink: String? { actionData?["url"] }
    var externalLinkLabel: String? { actionData?["label"] }

    var urgency: StepUrgency {
        if actionType == "urgent" || actionType == "critical" {
            return .immediate
        }
        if actionType == "warning" {
            return .soon
        }
        return .later
    }
}

// MARK: - Quick-Dial Contact

struct QuickDialContact: Codable, Identifiable {
    let name: String
    let phone: String
    let description: String

    var id: String { "\(name)-\(phone)" }

    static let defaults: [QuickDialContact] = [
        QuickDialContact(name: "Bank Fraud Hotline", phone: "", description: "Your bank's fraud department"),
        QuickDialContact(name: "FTC Report Fraud", phone: "1-877-382-4357", description: "Federal Trade Commission"),
        QuickDialContact(name: "Identity Theft Hotline", phone: "1-877-438-4338", description: "IdentityTheft.gov"),
    ]
}
