import SwiftUI

struct RecoveryView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var selectedCategory: ThreatCategory?
    @State private var checklist: RecoveryChecklist?
    @State private var completedStepIds: Set<String> = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showCallSheet = false

    var body: some View {
        ZStack(alignment: .bottomTrailing) {
            mainContent
            callForHelpFAB
        }
        .background(Color.neutral50.ignoresSafeArea())
        .navigationTitle("I Already Clicked It")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Close") { dismiss() }
            }
        }
        .sheet(isPresented: $showCallSheet) {
            callForHelpSheet
        }
        .alert("Error", isPresented: .constant(errorMessage != nil)) {
            Button("OK") { errorMessage = nil }
        } message: {
            Text(errorMessage ?? "")
        }
    }

    // MARK: - Main Content

    @ViewBuilder
    private var mainContent: some View {
        if let checklist {
            checklistView(checklist)
        } else {
            categorySelectionView
        }
    }

    // MARK: - Category Selection (Triage)

    private var categorySelectionView: some View {
        ScrollView {
            VStack(spacing: Spacing.lg) {
                calmingHeader

                ForEach(ThreatCategory.allCases) { category in
                    Button {
                        Task { await loadChecklist(for: category) }
                    } label: {
                        HStack(spacing: Spacing.md) {
                            Image(systemName: category.iconName)
                                .font(.system(size: 22))
                                .foregroundColor(.severityCritical)
                                .frame(width: 40)

                            Text(category.displayName)
                                .font(AppFont.body())
                                .foregroundColor(.neutral900)
                                .multilineTextAlignment(.leading)

                            Spacer()

                            if isLoading && selectedCategory == category {
                                ProgressView()
                            } else {
                                Image(systemName: "chevron.right")
                                    .foregroundColor(.neutral400)
                            }
                        }
                        .cardStyle()
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, Spacing.md)
            .padding(.bottom, 80)
        }
    }

    private var calmingHeader: some View {
        VStack(spacing: Spacing.sm) {
            Image(systemName: "heart.text.clipboard")
                .font(.system(size: 40))
                .foregroundColor(.severityCritical)

            Text("Don't worry — let's fix this together.")
                .font(AppFont.h2())
                .foregroundColor(.neutral900)
                .multilineTextAlignment(.center)

            Text("Tell us what happened so we can guide you through the next steps.")
                .font(AppFont.bodySmall())
                .foregroundColor(.neutral500)
                .multilineTextAlignment(.center)
        }
        .padding(.vertical, Spacing.md)
    }

    // MARK: - Checklist View

    private func checklistView(_ list: RecoveryChecklist) -> some View {
        ScrollView {
            VStack(spacing: Spacing.lg) {
                progressBar(list)

                Text(list.title)
                    .font(AppFont.h2())
                    .foregroundColor(.neutral900)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, Spacing.md)

                ForEach(list.steps) { step in
                    stepCard(step)
                }

                disclaimerSection

                Button("Start Over") {
                    withAnimation {
                        checklist = nil
                        completedStepIds = []
                        selectedCategory = nil
                    }
                }
                .font(AppFont.bodySmall())
                .foregroundColor(.neutral500)
                .padding(.bottom, 80)
            }
            .padding(.horizontal, Spacing.md)
        }
    }

    // MARK: - Progress Bar

    private func progressBar(_ list: RecoveryChecklist) -> some View {
        let total = list.steps.count
        let completed = completedStepIds.count
        let fraction = total > 0 ? Double(completed) / Double(total) : 0

        return VStack(spacing: Spacing.xs) {
            HStack {
                Text("Progress")
                    .font(AppFont.bodySmall())
                    .foregroundColor(.neutral600)
                Spacer()
                Text("\(completed) of \(total) steps")
                    .font(AppFont.bodySmall())
                    .foregroundColor(.neutral500)
            }

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.neutral200)
                        .frame(height: 8)

                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.severitySafe)
                        .frame(width: geo.size.width * fraction, height: 8)
                        .animation(.easeInOut, value: fraction)
                }
            }
            .frame(height: 8)
        }
        .padding(.horizontal, Spacing.md)
        .padding(.top, Spacing.sm)
    }

    // MARK: - Step Card

    private func stepCard(_ step: RecoveryStep) -> some View {
        let isDone = completedStepIds.contains(step.id)

        return VStack(alignment: .leading, spacing: Spacing.sm) {
            HStack {
                Text(step.urgency.displayName)
                    .font(AppFont.caption())
                    .foregroundColor(urgencyColor(step.urgency))
                    .padding(.horizontal, Spacing.sm)
                    .padding(.vertical, 2)
                    .background(urgencyColor(step.urgency).opacity(0.1))
                    .cornerRadius(4)

                Spacer()

                if isDone {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.severitySafe)
                }
            }

            Text(step.title)
                .font(AppFont.h2())
                .foregroundColor(isDone ? .neutral400 : .neutral900)
                .strikethrough(isDone)

            Text(step.description)
                .font(AppFont.body())
                .foregroundColor(isDone ? .neutral400 : .neutral700)

            if !isDone {
                Button {
                    withAnimation {
                        completedStepIds.insert(step.id)
                    }
                } label: {
                    Text("Done")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(PrimaryButtonStyle(backgroundColor: .severitySafe))
            }
        }
        .cardStyle()
    }

    private func urgencyColor(_ urgency: StepUrgency) -> Color {
        switch urgency {
        case .immediate: return .severityCritical
        case .soon:      return .severityMedium
        case .later:     return .severityInfo
        }
    }

    // MARK: - Disclaimer

    private var disclaimerSection: some View {
        Text("This guidance is informational and not a substitute for professional security or legal advice.")
            .font(AppFont.caption())
            .foregroundColor(.neutral400)
            .multilineTextAlignment(.center)
            .padding(.horizontal, Spacing.md)
    }

    // MARK: - Call for Help FAB

    private var callForHelpFAB: some View {
        Button { showCallSheet = true } label: {
            HStack(spacing: Spacing.sm) {
                Image(systemName: "phone.fill")
                Text("Call for Help")
                    .font(AppFont.body())
            }
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.lg)
            .padding(.vertical, Spacing.md)
            .background(Color.severityCritical)
            .cornerRadius(28)
            .shadow(color: .severityCritical.opacity(0.3), radius: 8, x: 0, y: 4)
        }
        .padding(Spacing.lg)
    }

    // MARK: - Call for Help Sheet

    private var callForHelpSheet: some View {
        NavigationStack {
            List {
                Section {
                    Text("If you're in immediate danger, call 911.")
                        .font(AppFont.body())
                        .foregroundColor(.severityCritical)
                }

                Section("Helpful Numbers") {
                    ForEach(QuickDialContact.defaults) { contact in
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(contact.name)
                                .font(AppFont.body())
                                .foregroundColor(.neutral900)
                            Text(contact.description)
                                .font(AppFont.caption())
                                .foregroundColor(.neutral500)
                            if !contact.phone.isEmpty {
                                Link(contact.phone, destination: URL(string: "tel:\(contact.phone)")!)
                                    .font(AppFont.body())
                                    .foregroundColor(.severityInfo)
                            }
                        }
                        .padding(.vertical, Spacing.xs)
                    }
                }

                Section("Family Alert") {
                    Button {
                        // Placeholder for family alert feature
                    } label: {
                        HStack {
                            Image(systemName: "person.2.fill")
                            Text("Alert a family member")
                        }
                    }
                }
            }
            .navigationTitle("Get Help")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") { showCallSheet = false }
                }
            }
        }
    }

    // MARK: - Data Loading

    private func loadChecklist(for category: ThreatCategory) async {
        selectedCategory = category
        isLoading = true
        errorMessage = nil

        do {
            let result = try await APIClient.shared.getChecklist(for: category)
            withAnimation {
                checklist = result
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}

#Preview {
    NavigationStack {
        RecoveryView()
    }
}
