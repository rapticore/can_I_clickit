import SwiftUI

struct ScanHistoryView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var history: [ScanHistoryEntry] = []
    @State private var selectedResult: ScanResult?
    @State private var selectedPreview: String = ""

    var body: some View {
        Group {
            if history.isEmpty {
                emptyState
            } else {
                historyList
            }
        }
        .background(Color.neutral50.ignoresSafeArea())
        .navigationTitle("History")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Close") { dismiss() }
            }
            if !history.isEmpty {
                ToolbarItem(placement: .destructiveAction) {
                    Button("Clear") {
                        history = []
                        ScanHistoryStore.save([])
                    }
                    .foregroundColor(.severityCritical)
                }
            }
        }
        .onAppear {
            history = ScanHistoryStore.load()
        }
        .sheet(item: $selectedResult) { result in
            NavigationStack {
                VerdictView(result: result, inputPreview: selectedPreview)
            }
        }
    }

    // MARK: - Empty State

    private var emptyState: some View {
        VStack(spacing: Spacing.md) {
            Image(systemName: "clock.arrow.circlepath")
                .font(.system(size: 48))
                .foregroundColor(.neutral300)

            Text("No scans yet")
                .font(AppFont.h2())
                .foregroundColor(.neutral500)

            Text("Your scan history will appear here.")
                .font(AppFont.bodySmall())
                .foregroundColor(.neutral400)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // MARK: - History List

    private var historyList: some View {
        List {
            ForEach(history) { entry in
                Button {
                    selectedPreview = entry.inputPreview
                    selectedResult = entry.result
                } label: {
                    historyRow(entry)
                }
            }
            .onDelete(perform: deleteEntries)
        }
        .listStyle(.plain)
    }

    private func historyRow(_ entry: ScanHistoryEntry) -> some View {
        HStack(spacing: Spacing.md) {
            verdictBadge(entry.result.threatLevel)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(entry.inputPreview)
                    .font(AppFont.bodySmall())
                    .foregroundColor(.neutral900)
                    .lineLimit(2)

                HStack(spacing: Spacing.sm) {
                    Image(systemName: entry.scanType.iconName)
                        .font(.system(size: 11))
                        .foregroundColor(.neutral400)

                    Text(entry.scanType.displayName)
                        .font(AppFont.caption())
                        .foregroundColor(.neutral400)

                    Text("·")
                        .foregroundColor(.neutral300)

                    Text(entry.createdAt, style: .relative)
                        .font(AppFont.caption())
                        .foregroundColor(.neutral400)
                }
            }

            Spacer()

            Image(systemName: "chevron.right")
                .font(.system(size: 12))
                .foregroundColor(.neutral300)
        }
        .padding(.vertical, Spacing.xs)
    }

    private func verdictBadge(_ level: ThreatLevel) -> some View {
        let color: Color = {
            switch level {
            case .safe:       return .severitySafe
            case .suspicious: return .severityMedium
            case .dangerous:  return .severityCritical
            }
        }()

        return Text(level.displayName)
            .font(.system(size: 11, weight: .semibold))
            .foregroundColor(color)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(color.opacity(0.1))
            .cornerRadius(4)
    }

    private func deleteEntries(at offsets: IndexSet) {
        history.remove(atOffsets: offsets)
        ScanHistoryStore.save(history)
    }
}

#Preview {
    NavigationStack {
        ScanHistoryView()
    }
}
