import Foundation
import AVFoundation
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let asset = AVURLAsset(url: url)
let gen = AVAssetImageGenerator(asset: asset)
gen.requestedTimeToleranceBefore = .zero
gen.requestedTimeToleranceAfter = .zero
var checked = 0
for i in 0..<20 {
    let img = try gen.copyCGImage(at: CMTime(value: Int64(i), timescale: 20), actualTime: nil)
    if img.width != 256 || img.height != 144 { fatalError("Unexpected frame dimensions") }
    checked += 1
}
print("Locally decoded \(checked) MP4 frames at 256x144 using AVFoundation")
