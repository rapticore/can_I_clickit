import ProjectDescription

let project = Project(
    name: "CanIClickIt",
    organizationName: "CanIClickIt",
    targets: [
        .target(
            name: "CanIClickIt",
            destinations: [.iPhone, .iPad],
            product: .app,
            bundleId: "com.caniclickit.app",
            deploymentTargets: .iOS("16.0"),
            infoPlist: .extendingDefault(
                with: [
                    "CFBundleDisplayName": "Can I Click It?",
                    "UILaunchScreen": [:],
                    "UISupportedInterfaceOrientations": [
                        "UIInterfaceOrientationPortrait",
                    ],
                    "NSMicrophoneUsageDescription": "Microphone access is used for voice input.",
                    "NSSpeechRecognitionUsageDescription": "Speech recognition is used to transcribe voice input.",
                    "NSCameraUsageDescription": "Camera access is used for QR code scanning.",
                ]
            ),
            sources: ["CanIClickIt/**/*.swift"],
            resources: []
        ),
    ]
)
