/// <reference types="node" />
export interface WitaiOptions {
    key?: string;
}
export declare function resolveSpeechWithWitai(audioBuffer: Buffer, options?: WitaiOptions): Promise<string>;
