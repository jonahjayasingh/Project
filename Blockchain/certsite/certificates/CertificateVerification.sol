// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateVerification {

    mapping(bytes32 => bool) private certificates;

    function issueCertificate(bytes32 certHash) public {
        certificates[certHash] = true;
    }

    function verifyCertificate(bytes32 certHash)
        public
        view
        returns (bool)
    {
        return certificates[certHash];
    }
}
