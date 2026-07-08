import SwiftUI

/// Stores LiveKit connection credentials in UserDefaults
struct LiveKitCredentials: Codable {
    var serverUrl: String = ""
    var token: String = ""
    var roomName: String = "test-room"
    
    static let defaultsKey = "LiveKitCredentials"
    
    static func load() -> LiveKitCredentials {
        guard let data = UserDefaults.standard.data(forKey: defaultsKey),
              let creds = try? JSONDecoder().decode(LiveKitCredentials.self, from: data)
        else { return LiveKitCredentials() }
        return creds
    }
    
    func save() {
        guard let data = try? JSONEncoder().encode(self) else { return }
        UserDefaults.standard.set(data, forKey: LiveKitCredentials.defaultsKey)
    }
}

struct SettingsView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var serverUrl: String = ""
    @State private var token: String = ""
    @State private var roomName: String = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("LiveKit Cloud")) {
                    TextField("Server URL", text: $serverUrl)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                        .keyboardType(.URL)
                    TextField("Room Name", text: $roomName)
                        .autocapitalization(.none)
                    SecureField("Token", text: $token)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                }
                
                Section(footer: Text("Get these from your LiveKit Cloud project dashboard. The token must have room join permissions.")) {
                    Button("Save") {
                        var creds = LiveKitCredentials()
                        creds.serverUrl = serverUrl
                        creds.token = token
                        creds.roomName = roomName
                        creds.save()
                        dismiss()
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(serverUrl.isEmpty || token.isEmpty)
                }
                
                if !serverUrl.isEmpty || !token.isEmpty {
                    Section {
                        Button("Clear Saved Credentials", role: .destructive) {
                            serverUrl = ""
                            token = ""
                            roomName = "test-room"
                            LiveKitCredentials().save()
                        }
                    }
                }
            }
            .navigationTitle("Connection Settings")
            .onAppear {
                let creds = LiveKitCredentials.load()
                serverUrl = creds.serverUrl
                token = creds.token
                roomName = creds.roomName
            }
        }
    }
}
