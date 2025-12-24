// Citizen credential circuit
// This is a simplified template - production would use proper Circom syntax

pragma circom 2.0.0;

include "circomlib/circuits/poseidon.circom";
include "circomlib/circuits/comparators.circom";

template CitizenCredential() {
    // Private inputs (not revealed)
    signal input citizenSecret;       // Citizen's secret key
    signal input citizenId;           // Citizen's ID (hashed)
    signal input birthYear;           // For age verification
    signal input registrationDate;    // Date of registration
    
    // Public inputs (revealed but verified)
    signal input currentYear;         // Current year for age check
    signal input minAge;              // Minimum voting age
    signal input registrationCutoff;  // Must be registered before this
    
    // Outputs
    signal output nullifierHash;      // Unique identifier for this vote
    signal output credentialHash;     // Anonymous credential
    
    // Age verification: birthYear + minAge <= currentYear
    component ageCheck = LessEqThan(32);
    ageCheck.in[0] <== birthYear + minAge;
    ageCheck.in[1] <== currentYear;
    ageCheck.out === 1;
    
    // Registration verification: registrationDate <= registrationCutoff
    component regCheck = LessEqThan(32);
    regCheck.in[0] <== registrationDate;
    regCheck.in[1] <== registrationCutoff;
    regCheck.out === 1;
    
    // Generate nullifier hash (prevents double voting)
    component nullifier = Poseidon(2);
    nullifier.inputs[0] <== citizenSecret;
    nullifier.inputs[1] <== citizenId;
    nullifierHash <== nullifier.out;
    
    // Generate credential hash
    component credential = Poseidon(3);
    credential.inputs[0] <== citizenSecret;
    credential.inputs[1] <== nullifierHash;
    credential.inputs[2] <== currentYear;
    credentialHash <== credential.out;
}

component main {public [currentYear, minAge, registrationCutoff]} = CitizenCredential();
