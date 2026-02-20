import SwiftUI
import AVFoundation

struct QRScannerView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var scannedCode: String?
    @State private var scanResult: ScanResult?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showVerdict = false
    @State private var isTorchOn = false

    var body: some View {
        ZStack {
            CameraPreviewView(scannedCode: $scannedCode, isTorchOn: $isTorchOn)
                .ignoresSafeArea()

            scannerOverlay

            if isLoading {
                Color.black.opacity(0.5).ignoresSafeArea()
                VStack(spacing: Spacing.md) {
                    ProgressView()
                        .scaleEffect(1.5)
                        .tint(.white)
                    Text("Analyzing...")
                        .font(AppFont.body())
                        .foregroundColor(.white)
                }
            }
        }
        .navigationTitle("Scan QR Code")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Close") { dismiss() }
            }
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    isTorchOn.toggle()
                } label: {
                    Image(systemName: isTorchOn ? "flashlight.on.fill" : "flashlight.off.fill")
                        .foregroundColor(.white)
                }
            }
        }
        .onChange(of: scannedCode) { _, newValue in
            if let code = newValue {
                Task { await handleScannedCode(code) }
            }
        }
        .sheet(isPresented: $showVerdict) {
            if let result = scanResult {
                NavigationStack {
                    VerdictView(result: result, inputPreview: scannedCode ?? "")
                }
            }
        }
        .alert("Error", isPresented: .constant(errorMessage != nil)) {
            Button("OK") {
                errorMessage = nil
                scannedCode = nil
            }
        } message: {
            Text(errorMessage ?? "")
        }
    }

    // MARK: - Scanner Overlay

    private var scannerOverlay: some View {
        VStack {
            Spacer()

            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.white.opacity(0.8), lineWidth: 3)
                .frame(width: 250, height: 250)
                .background(Color.clear)

            Spacer()

            Text("Point your camera at a QR code")
                .font(AppFont.body())
                .foregroundColor(.white)
                .padding(.horizontal, Spacing.lg)
                .padding(.vertical, Spacing.md)
                .background(Color.black.opacity(0.6))
                .cornerRadius(8)
                .padding(.bottom, Spacing.xl)
        }
    }

    // MARK: - Handle Scan

    private func handleScannedCode(_ code: String) async {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil

        let scanType: ScanType = code.hasPrefix("http://") || code.hasPrefix("https://") ? .url : .qrCode
        let request = ScanRequest(content: code, type: scanType)

        do {
            let result = try await APIClient.shared.scan(request)
            scanResult = result
            showVerdict = true
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}

// MARK: - Camera Preview (AVFoundation)

struct CameraPreviewView: UIViewRepresentable {
    @Binding var scannedCode: String?
    @Binding var isTorchOn: Bool

    func makeUIView(context: Context) -> CameraPreviewUIView {
        let view = CameraPreviewUIView()
        view.delegate = context.coordinator
        return view
    }

    func updateUIView(_ uiView: CameraPreviewUIView, context: Context) {
        uiView.setTorch(on: isTorchOn)
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(scannedCode: $scannedCode)
    }

    class Coordinator: NSObject, AVCaptureMetadataOutputObjectsDelegate {
        @Binding var scannedCode: String?
        private var lastScanned: Date = .distantPast

        init(scannedCode: Binding<String?>) {
            _scannedCode = scannedCode
        }

        func metadataOutput(_ output: AVCaptureMetadataOutput, didOutput metadataObjects: [AVMetadataObject], from connection: AVCaptureConnection) {
            guard Date().timeIntervalSince(lastScanned) > 2.0,
                  let object = metadataObjects.first as? AVMetadataMachineReadableCodeObject,
                  let value = object.stringValue else { return }

            lastScanned = Date()
            DispatchQueue.main.async {
                self.scannedCode = value
            }
        }
    }
}

class CameraPreviewUIView: UIView {
    weak var delegate: AVCaptureMetadataOutputObjectsDelegate?

    private let captureSession = AVCaptureSession()
    private var previewLayer: AVCaptureVideoPreviewLayer?

    override func layoutSubviews() {
        super.layoutSubviews()
        previewLayer?.frame = bounds
    }

    override func didMoveToSuperview() {
        super.didMoveToSuperview()
        if superview != nil {
            setupCamera()
        }
    }

    func setTorch(on: Bool) {
        guard let device = AVCaptureDevice.default(for: .video),
              device.hasTorch else { return }
        try? device.lockForConfiguration()
        device.torchMode = on ? .on : .off
        device.unlockForConfiguration()
    }

    private func setupCamera() {
        guard let device = AVCaptureDevice.default(for: .video),
              let input = try? AVCaptureDeviceInput(device: device) else { return }

        if captureSession.canAddInput(input) {
            captureSession.addInput(input)
        }

        let output = AVCaptureMetadataOutput()
        if captureSession.canAddOutput(output) {
            captureSession.addOutput(output)
            output.setMetadataObjectsDelegate(delegate, queue: .main)
            output.metadataObjectTypes = [.qr]
        }

        let layer = AVCaptureVideoPreviewLayer(session: captureSession)
        layer.videoGravity = .resizeAspectFill
        layer.frame = bounds
        self.layer.addSublayer(layer)
        previewLayer = layer

        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.captureSession.startRunning()
        }
    }
}

#Preview {
    NavigationStack {
        QRScannerView()
    }
}
