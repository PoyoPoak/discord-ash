"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getDurationFromMonoBuffer = exports.convertStereoToMono = void 0;
/**
 * Convert stereo audio buffer to mono
 * @param input Buffer of stereo audio
 * @returns
 */
function convertStereoToMono(input) {
    const stereoData = new Int16Array(input);
    const monoData = new Int16Array(stereoData.length / 2);
    for (let i = 0, j = 0; i < stereoData.length; i += 4) {
        monoData[j] = stereoData[i];
        j += 1;
        monoData[j] = stereoData[i + 1];
        j += 1;
    }
    return Buffer.from(monoData);
}
exports.convertStereoToMono = convertStereoToMono;
function getDurationFromMonoBuffer(buffer) {
    const duration = buffer.length / 48000 / 2;
    return duration;
}
exports.getDurationFromMonoBuffer = getDurationFromMonoBuffer;
//# sourceMappingURL=audio.js.map