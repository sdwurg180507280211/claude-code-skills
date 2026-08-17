import Foundation
import Vision
import AppKit

// 用法: swift ocr_wechat.swift <截图路径>
// 输出: x,y widthxheight<TAB>识别文本
// 用于微信界面（uiautomator 被屏蔽，但截图可用）的中文 OCR 定位。

let path = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "/tmp/screen.png"
guard let img = NSImage(contentsOfFile: path),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("cannot load image")
    exit(1)
}

let request = VNRecognizeTextRequest { req, error in
    guard error == nil else { return }
    guard let observations = req.results as? [VNRecognizedTextObservation] else { return }
    for obs in observations {
        guard let candidate = obs.topCandidates(1).first else { continue }
        let bb = obs.boundingBox
        let x = bb.origin.x * CGFloat(cg.width)
        let y = (1 - bb.origin.y - bb.height) * CGFloat(cg.height)
        let w = bb.width * CGFloat(cg.width)
        let h = bb.height * CGFloat(cg.height)
        print(String(format: "%.0f,%.0f %.0fx%.0f\t%@", x, y, w, h, candidate.string))
    }
}

request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
try? handler.perform([request])
