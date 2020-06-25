#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from datetime import datetime

ddo_sample = {
    "@context": "https://w3id.org/future-method/v1",
    "id": "did:op:cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888865",
    "dataToken": "0x2eD6d94Ec5Af12C43B924572F9aFFe470DC83282",
    "created": datetime.strptime("2016-02-08T16:02:20Z", '%Y-%m-%dT%H:%M:%SZ'),
    "publicKey": [
        {
            "id": "did:op:b6e2eb5eff1a093ced9826315d5a4ef6c5b5c8bd3c49890ee284231d7e1d0aaa#keys-1",
            "type": "RsaVerificationKey2018",
            "owner": "did:op:6027c1e7cbae06a91fce0557ee53195284825f56a7100be0c53cbf4391aa26cc",
            "publicKeyPem": "-----BEGIN PUBLIC KEY...END PUBLIC KEY-----\r\n"
        },
        {
            "id": "did:op:d1fe2dc63e0e4fe2fff65d2077d71e39eef3ceda293a36265acc30c81d78ce95#keys-2",
            "type": "Ed25519VerificationKey2018",
            "owner": "did:op:4c27a254e607cdf91a1206480e7eb8c74856102316c1a462277d4f21c02373b6",
            "publicKeyBase58": "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
        },
        {
            "id": "did:op:da1ec6bba5ab6842897599cb8e6c17b888e3fee1e8adb2ac18e30c6b511a78b8#keys-3",
            "type": "RsaPublicKeyExchangeKey2018",
            "owner": "did:op:5f6b885202ffb9643874be529302eb00d55e226959f1fbacaeda592c5b5c9484",
            "publicKeyPem": "-----BEGIN PUBLIC KEY...END PUBLIC KEY-----\r\n"
        }
    ],
    "authentication": [
        {
            "type": "RsaSignatureAuthentication2018",
            "publicKey": "did:op:0ebed8226ada17fde24b6bf2b95d27f8f05fcce09139ff5cec31f6d81a7cd2ea"
                         "#keys-1"
        },
        {
            "type": "ieee2410Authentication2018",
            "publicKey": "did:op:c24997ab64005abbe0bee5f6ad8dc4038c27d52b6e4a1f537a488441a9c2b0b9"
                         "#keys-2"
        }
    ],
    "proof": {
        "type": "UUIDSignature",
        "created": datetime.strptime("2016-02-08T16:02:20Z", '%Y-%m-%dT%H:%M:%SZ'),
        "creator": "did:example:8uQhQMGzWxR8vw5P3UWH1ja",
        "signatureValue": "QNB13Y7Q9...1tzjn4w=="
    },
    "service": [
        {
            "type": "Access",
            "purchaseEndpoint": "http://localhost:8030/api/v1/brizo/services/access/purchase?",
            "serviceEndpoint": "http://localhost:8030/api/v1/brizo/services/consume?pubKey"
                               "=0x00bd138abd70e2f00903268f3db08f2d25677c9e&agreementId"
                               "=0xeb4bb084942044a3857a5d107b48563a1ab56608c79342319697710336484fca&url=0",
            "attributes": {
                "main": {
                    "cost": "10",
                    "timeout": 0
                }
            }
        },
        {
            "type": "Compute",
            "serviceEndpoint": "http://mybrizo.org/api/v1/brizo/services/compute?pubKey=${"
                               "pubKey}&agreementId={agreementId}&algo={algo}&container={container}",
            "attributes": {
                "main": {
                    "cost": "5",
                    "timeout": 3600
                }
            }
        },
        {
            "type": "Metadata",
            "serviceEndpoint": "http://myaquarius.org/api/v1/provider/assets/metadata/{did}",
            "attributes": {
                "main": {
                    "name": "UK Weather information 2011",
                    "type": "dataset",
                    "dateCreated": datetime.strptime("2016-02-08T16:02:20Z", '%Y-%m-%dT%H:%M:%SZ'),
                    "datePublished": datetime.strptime("2016-02-08T16:02:20Z", '%Y-%m-%dT%H:%M:%SZ'),
                    "author": "Met Office",
                    "license": "CC-BY",
                    "files": [
                        {
                            "url": "https://testocnfiles.blob.core.windows.net/testfiles/testzkp"
                                   ".pdf",
                            "contentType": "text/csv",
                            "checksum": "efb2c764274b745f5fc37f97c6b0e761",
                            "contentLength": "4535431",
                            "resourceId": "access-log2018-02-13-15-17-29-18386C502CAEA932"
                        }
                    ]
                },
                "curation": {
                    "rating": 0.93,
                    "numVotes": 123,
                    "schema": "Binary Votting"
                },
                "additionalInformation": {
                    "description": "Weather information of UK including temperature and humidity",
                    "copyrightHolder": "Met Office",
                    "categories": ["weather", "meteorology"],
                    "workExample": "423432fsd,51.509865,-0.118092,2011-01-01T10:55:11+00:00,7.2,68",
                    "links": [
                        {
                            "type": "sample",
                            "sample1":
                                "http://data.ceda.ac.uk/badc/ukcp09/data/gridded-land-obs/gridded"
                                "-land-obs-daily/"
                        },
                        {
                            "sample2":
                                "http://data.ceda.ac.uk/badc/ukcp09/data/gridded-land-obs/gridded"
                                "-land-obs-averages-25km/"
                        },
                        {
                            "fieldsDescription": "http://data.ceda.ac.uk/badc/ukcp09/"
                        }
                    ],
                    "inLanguage": "en",
                    "tags": "weather, uk, 2011, temperature, humidity",
                    "customField": "customValue"
                }
            }
        }
    ]
}
