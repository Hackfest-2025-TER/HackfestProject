import { groth16 } from 'snarkjs';

self.onmessage = async (e) => {
    const { input, wasmPath, zkeyPath } = e.data;
    try {
        console.log("Worker: Starting proof generation...");
        const { proof, publicSignals } = await groth16.fullProve(input, wasmPath, zkeyPath);
        console.log("Worker: Proof generated successfully");
        postMessage({ type: 'RESULT', proof, publicSignals });
    } catch (err) {
        console.error("Worker Error:", err);
        postMessage({ type: 'ERROR', error: err.message });
    }
};
