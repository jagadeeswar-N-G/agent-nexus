/**
 * Ed25519 Cryptographic Utilities
 * For agent authentication via signature verification
 */

import nacl from 'tweetnacl';
import { encodeBase64, decodeBase64 } from 'tweetnacl-util';

export interface Keypair {
  publicKey: string;  // Base64-encoded
  privateKey: string; // Base64-encoded
}

/**
 * Generate a new Ed25519 keypair
 */
export function generateKeypair(): Keypair {
  const keypair = nacl.sign.keyPair();

  return {
    publicKey: encodeBase64(keypair.publicKey),
    privateKey: encodeBase64(keypair.secretKey),
  };
}

/**
 * Derive public key from private key
 */
export function getPublicKeyFromPrivate(privateKeyB64: string): string {
  try {
    const privateKey = decodeBase64(privateKeyB64);
    const keypair = nacl.sign.keyPair.fromSecretKey(privateKey);
    return encodeBase64(keypair.publicKey);
  } catch (error) {
    throw new Error('Invalid private key format');
  }
}

/**
 * Sign a challenge with private key
 * Returns detached signature (not including the message)
 */
export function signChallenge(challengeB64: string, privateKeyB64: string): string {
  try {
    const challenge = decodeBase64(challengeB64);
    const privateKey = decodeBase64(privateKeyB64);

    // Create detached signature
    const signature = nacl.sign.detached(challenge, privateKey);

    return encodeBase64(signature);
  } catch (error) {
    throw new Error('Failed to sign challenge');
  }
}

/**
 * Verify a signature (client-side verification, optional)
 */
export function verifySignature(
  messageB64: string,
  signatureB64: string,
  publicKeyB64: string
): boolean {
  try {
    const message = decodeBase64(messageB64);
    const signature = decodeBase64(signatureB64);
    const publicKey = decodeBase64(publicKeyB64);

    return nacl.sign.detached.verify(message, signature, publicKey);
  } catch (error) {
    return false;
  }
}

/**
 * Export keypair as JSON file
 */
export function exportKeypairAsJSON(keypair: Keypair, filename = 'agent-keypair.json'): void {
  const data = JSON.stringify(keypair, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Import keypair from JSON file
 */
export function importKeypairFromJSON(file: File): Promise<Keypair> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);

        if (!data.publicKey || !data.privateKey) {
          reject(new Error('Invalid keypair file format'));
          return;
        }

        resolve({
          publicKey: data.publicKey,
          privateKey: data.privateKey,
        });
      } catch (error) {
        reject(new Error('Failed to parse keypair file'));
      }
    };

    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

/**
 * Validate keypair format
 */
export function isValidKeypair(keypair: Keypair): boolean {
  try {
    const publicKey = decodeBase64(keypair.publicKey);
    const privateKey = decodeBase64(keypair.privateKey);

    // Ed25519 public key should be 32 bytes
    if (publicKey.length !== 32) return false;

    // Ed25519 private key should be 64 bytes (32 bytes seed + 32 bytes public key)
    if (privateKey.length !== 64) return false;

    // Verify that the public key matches the private key
    const derivedKeypair = nacl.sign.keyPair.fromSecretKey(privateKey);
    const derivedPublicKey = encodeBase64(derivedKeypair.publicKey);

    return derivedPublicKey === keypair.publicKey;
  } catch (error) {
    return false;
  }
}
