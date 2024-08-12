//
//  ContentView.swift
//  TextToNano
//
//  Created by David Navarro on 8/10/24.
//

import SwiftUI

struct ContentView: View {
    @State private var textToSend: String = ""
    @State private var serverIP: String = "192.168.1.xxx"   // replace with nanos ip
    
    var body: some View {
        VStack {
            TextField("Enter text:", text: $textToSend)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding()
            
            Button("Send to LCD") {
                sendTextToESP32()
            }
            .padding()
        }
        .padding()
    }
    
    func sendTextToESP32() {
        guard let url = URL(string: "http://\(serverIP)/") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let postString = "text=\(textToSend.replacingOccurrences(of: " ", with: "%20"))"
        request.httpBody = postString.data(using: .utf8)
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: \(error)")
                return
            }
            if let response = response as? HTTPURLResponse, response.statusCode == 200 {
                print("Text sent successfully!")
            }
        }
        
        task.resume()
    }
}

#Preview {
    ContentView()
}
