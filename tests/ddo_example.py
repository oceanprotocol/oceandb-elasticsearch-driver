from datetime import datetime

ddo_sample = {
    "@context": "https://w3id.org/future-method/v1",
    "id": "did:op:cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888865",
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
            "serviceDefinitionId": "0",
            "templateId": "0x044852b2a670ade5407e78fb2863c51de9fcb96542a07186fe3aeda6bb8a116d",
            "serviceAgreementContract": {
                "contractName": "ServiceExecutionAgreement",
                "fulfillmentOperator": 1,
                "events": [
                    {
                        "name": "AgreementInitialized",
                        "actorType": "consumer",
                        "handler": {
                            "moduleName": "payment",
                            "functionName": "lockPayment",
                            "version": "0.1"
                        }
                    }
                ]
            },
            "conditions": [
                {
                    "name": "lockPayment",
                    "contractName": "PaymentConditions",
                    "functionName": "lockPayment",
                    "timeout": 0,
                    "index": 0,
                    "conditionKey":
                        "0x2165e057ca19e807eaa52b6d5f82024021d1c1fbf92d3c53d2eb8a1a4de42d3f",
                    "parameters": [
                        {
                            "name": "assetId",
                            "type": "bytes32",
                            "value":
                                "cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888865"
                        },
                        {
                            "name": "price",
                            "type": "uint256",
                            "value": "10"
                        }
                    ],
                    "events": [
                        {
                            "name": "PaymentReleased",
                            "actorType": [
                                "consumer"
                            ],
                            "handlers": {
                                "moduleName": "serviceAgreement",
                                "functionName": "fulfillAgreement",
                                "version": "0.1"
                            }
                        }
                    ],
                    "dependencies": [],
                    "dependencyTimeoutFlags": [],
                    "isTerminalCondition": 0
                },
                {
                    "name": "grantAccess",
                    "contractName": "AccessConditions",
                    "functionName": "grantAccess",
                    "timeout": 10,
                    "index": 1,
                    "conditionKey":
                        "0x5c0b248ab89b89638a6ef7020afbe7390c90c1debebfb93f06577a221e455655",
                    "parameters": [
                        {
                            "name": "documentKeyId",
                            "type": "bytes32",
                            "value":
                                "cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888865"
                        }
                    ],
                    "events": [
                        {
                            "name": "PaymentReleased",
                            "actorType": [
                                "consumer"
                            ],
                            "handlers": {
                                "moduleName": "serviceAgreement",
                                "functionName": "fulfillAgreement",
                                "version": "0.1"
                            }
                        }
                    ],
                    "dependencies": [
                        {
                            "name": "lockPayment",
                            "timeout": 0
                        }
                    ],
                    "dependencyTimeoutFlags": [
                        0
                    ],
                    "isTerminalCondition": 0
                },
                {
                    "name": "releasePayment",
                    "contractName": "PaymentConditions",
                    "functionName": "releasePayment",
                    "timeout": 10,
                    "index": 2,
                    "conditionKey":
                        "0xc7b899951bb944225768dcc8173572e641b4b62aad4d1f42f59132c6f4eb9a62",
                    "parameters": [
                        {
                            "name": "assetId",
                            "type": "bytes32",
                            "value":
                                "cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888865"
                        },
                        {
                            "name": "price",
                            "type": "uint256",
                            "value": "10"
                        }
                    ],
                    "events": [
                        {
                            "name": "PaymentReleased",
                            "actorType": [
                                "consumer"
                            ],
                            "handlers": {
                                "moduleName": "serviceAgreement",
                                "functionName": "fulfillAgreement",
                                "version": "0.1"
                            }
                        }
                    ],
                    "dependencies": [
                        {
                            "name": "grantAccess",
                            "timeout": 0
                        }
                    ],
                    "dependencyTimeoutFlags": [
                        0
                    ],
                    "isTerminalCondition": 0
                },
                {
                    "name": "refundPayment",
                    "contractName": "PaymentConditions",
                    "functionName": "refundPayment",
                    "timeout": 10,
                    "index": 3,
                    "conditionKey":
                        "0x74901f13c534f069cb9523bacb4f617f4724a2910eae6a82f6fcec7adf28ac4c",
                    "parameters": [
                        {
                            "name": "assetId",
                            "type": "bytes32",
                            "value":
                                "cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888865"
                        },
                        {
                            "name": "price",
                            "type": "uint256",
                            "value": "10"
                        }
                    ],
                    "events": [
                        {
                            "name": "PaymentRefund",
                            "actorType": [
                                "consumer"
                            ],
                            "handlers": {
                                "moduleName": "serviceAgreement",
                                "functionName": "terminateAgreement",
                                "version": "0.1"
                            }
                        }
                    ],
                    "dependencies": [
                        {
                            "name": "lockPayment",
                            "timeout": 0
                        },
                        {
                            "name": "grantAccess",
                            "timeout": 86400
                        }
                    ],
                    "dependencyTimeoutFlags": [
                        0,
                        1
                    ],
                    "isTerminalCondition": 0
                }
            ]
        },
        {
            "type": "Compute",
            "serviceEndpoint": "http://mybrizo.org/api/v1/brizo/services/compute?pubKey=${"
                               "pubKey}&agreementId={agreementId}&algo={algo}&container={container}"
        },
        {
            "type": "Metadata",
            "serviceEndpoint": "http://myaquarius.org/api/v1/provider/assets/metadata/{did}",
            "metadata": {
                "base": {
                    "name": "UK Weather information 2011",
                    "type": "dataset",
                    "description": "Weather information of UK including temperature and humidity",
                    "size": "3.1gb",
                    "dateCreated": datetime.strptime("2016-02-08T16:02:20Z", '%Y-%m-%dT%H:%M:%SZ'),
                    "author": "Met Office",
                    "license": "CC-BY",
                    "copyrightHolder": "Met Office",
                    "encoding": "UTF-8",
                    "compression": "zip",
                    "categories": ["weather", "meteorology"],
                    "contentType": "text/csv",
                    "workExample": "423432fsd,51.509865,-0.118092,2011-01-01T10:55:11+00:00,7.2,68",
                    "files": [
                        {
                            "url": "https://testocnfiles.blob.core.windows.net/testfiles/testzkp"
                                   ".pdf",
                            "checksum": "efb2c764274b745f5fc37f97c6b0e761",
                            "contentLength": "4535431",
                            "resourceId": "access-log2018-02-13-15-17-29-18386C502CAEA932"
                        }
                    ],
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
                    "price": 10
                },
                "curation": {
                    "rating": 0.93,
                    "numVotes": 123,
                    "schema": "Binary Votting"
                },
                "additionalInformation": {
                    "updateFrecuency": "yearly",
                    "structuredMarkup": [
                        {
                            "uri": "http://skos.um.es/unescothes/C01194/jsonld",
                            "mediaType": "application/ld+json"
                        },
                        {
                            "uri": "http://skos.um.es/unescothes/C01194/turtle",
                            "mediaType": "text/turtle"
                        }
                    ]
                }
            }
        }
    ]
}
