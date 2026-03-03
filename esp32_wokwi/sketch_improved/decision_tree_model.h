#ifndef DECISION_TREE_MODEL_H
#define DECISION_TREE_MODEL_H
/*
 * decision_tree_model.h
 * =====================
 * Auto-generated Decision Tree model for ESP32 Embedded AI.
 *
 * Action classes:
 *   0 = GO_STRAIGHT   – path clear, drive forward
 *   1 = VEER_LEFT     – moderate left correction
 *   2 = VEER_RIGHT    – moderate right correction
 *   3 = HARD_LEFT     – sharp left / spin
 *   4 = HARD_RIGHT    – sharp right / spin
 *
 * Input: float f[9] – normalised sensor distances
 *   Index order: [LS, LF, LM, LN, C, RN, RM, RF, RS]
 *
 * Generated from 32000 training samples.
 * Classifier accuracy: 0.8652
 * Speed regressor MAE: 0.0478
 */

/* Action labels */
#define DT_GO_STRAIGHT  0
#define DT_VEER_LEFT    1
#define DT_VEER_RIGHT   2
#define DT_HARD_LEFT    3
#define DT_HARD_RIGHT   4

// Auto-generated Decision Tree  (depth=8, leaves=199, classes=5)
// Features: ['dLS', 'dLF', 'dLM', 'dLN', 'dC', 'dRN', 'dRM', 'dRF', 'dRS']
static int dt_predict_action(const float f[9]) {
    if (f[3] <= 1.9998f) {
        if (f[5] <= 0.3448f) {
            if (f[3] <= 0.2295f) {
                if (f[5] <= 0.1884f) {
                    if (f[3] <= 0.1492f) {
                        if (f[5] <= 0.1354f) {
                            if (f[3] <= 0.1228f) {
                                if (f[5] <= 0.1087f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                return 3;
                            }
                        } else {
                            if (f[2] <= 0.3955f) {
                                if (f[4] <= 0.3017f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                return 4;
                            }
                        }
                    } else {
                        if (f[2] <= 0.1779f) {
                            return 4;
                        } else {
                            if (f[0] <= 0.1616f) {
                                return 4;
                            } else {
                                if (f[5] <= 0.1816f) {
                                    return 3;
                                } else {
                                    return 3;
                                }
                            }
                        }
                    }
                } else {
                    if (f[8] <= 0.1693f) {
                        if (f[3] <= 0.1591f) {
                            if (f[0] <= 4.5334f) {
                                return 4;
                            } else {
                                return 3;
                            }
                        } else {
                            return 3;
                        }
                    } else {
                        if (f[7] <= 0.1721f) {
                            if (f[3] <= 0.1358f) {
                                return 4;
                            } else {
                                return 3;
                            }
                        } else {
                            if (f[3] <= 0.2033f) {
                                if (f[6] <= 0.1403f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[5] <= 0.2084f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    }
                }
            } else {
                if (f[1] <= 0.2329f) {
                    if (f[5] <= 0.1358f) {
                        if (f[2] <= 4.9160f) {
                            return 3;
                        } else {
                            return 4;
                        }
                    } else {
                        if (f[6] <= 0.3342f) {
                            if (f[1] <= 0.1822f) {
                                return 4;
                            } else {
                                return 3;
                            }
                        } else {
                            if (f[5] <= 0.2071f) {
                                if (f[1] <= 0.1690f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[8] <= 0.1198f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    }
                } else {
                    if (f[0] <= 0.2386f) {
                        if (f[5] <= 0.1579f) {
                            if (f[0] <= 0.1349f) {
                                if (f[1] <= 0.3906f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                return 3;
                            }
                        } else {
                            if (f[7] <= 0.2015f) {
                                return 3;
                            } else {
                                if (f[8] <= 0.1874f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    } else {
                        if (f[2] <= 0.2766f) {
                            if (f[5] <= 0.1702f) {
                                if (f[2] <= 0.1585f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[6] <= 0.2348f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        } else {
                            if (f[3] <= 0.2890f) {
                                if (f[5] <= 0.2664f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[5] <= 0.3225f) {
                                    return 3;
                                } else {
                                    return 3;
                                }
                            }
                        }
                    }
                }
            }
        } else {
            if (f[7] <= 0.3444f) {
                if (f[0] <= 0.2666f) {
                    if (f[7] <= 0.2253f) {
                        if (f[0] <= 0.2095f) {
                            if (f[1] <= 0.6631f) {
                                if (f[4] <= 0.6554f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                return 3;
                            }
                        } else {
                            if (f[3] <= 0.3134f) {
                                if (f[2] <= 0.2946f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                return 3;
                            }
                        }
                    } else {
                        if (f[0] <= 0.2433f) {
                            if (f[8] <= 0.2349f) {
                                if (f[0] <= 0.2297f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[7] <= 0.2309f) {
                                    return 4;
                                } else {
                                    return 4;
                                }
                            }
                        } else {
                            if (f[7] <= 0.2510f) {
                                if (f[8] <= 1.6340f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[8] <= 0.2661f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    }
                } else {
                    if (f[1] <= 0.2782f) {
                        if (f[7] <= 0.2529f) {
                            if (f[1] <= 0.2299f) {
                                if (f[7] <= 0.2146f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[3] <= 0.1845f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        } else {
                            if (f[8] <= 0.2346f) {
                                return 3;
                            } else {
                                if (f[6] <= 0.2505f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    } else {
                        if (f[3] <= 0.2521f) {
                            if (f[7] <= 0.1680f) {
                                if (f[3] <= 0.1203f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[8] <= 0.1547f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        } else {
                            if (f[2] <= 0.1863f) {
                                if (f[7] <= 0.1656f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[7] <= 0.3183f) {
                                    return 3;
                                } else {
                                    return 3;
                                }
                            }
                        }
                    }
                }
            } else {
                if (f[3] <= 0.3669f) {
                    if (f[8] <= 0.2244f) {
                        if (f[3] <= 0.1482f) {
                            if (f[8] <= 0.1419f) {
                                if (f[2] <= 3.6623f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                return 4;
                            }
                        } else {
                            if (f[2] <= 0.2069f) {
                                if (f[8] <= 0.1298f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[8] <= 0.1992f) {
                                    return 3;
                                } else {
                                    return 3;
                                }
                            }
                        }
                    } else {
                        if (f[6] <= 0.2481f) {
                            if (f[3] <= 0.1497f) {
                                if (f[6] <= 0.1144f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[2] <= 0.3606f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        } else {
                            if (f[3] <= 0.3514f) {
                                if (f[8] <= 0.3365f) {
                                    return 4;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[4] <= 0.7288f) {
                                    return 4;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    }
                } else {
                    if (f[1] <= 0.3504f) {
                        if (f[8] <= 0.2813f) {
                            if (f[1] <= 0.2715f) {
                                if (f[8] <= 0.2281f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[0] <= 0.2285f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        } else {
                            if (f[6] <= 0.2064f) {
                                if (f[1] <= 0.1960f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[8] <= 0.3352f) {
                                    return 4;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    } else {
                        if (f[0] <= 0.3501f) {
                            if (f[8] <= 0.2930f) {
                                if (f[0] <= 0.2595f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[6] <= 0.2275f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        } else {
                            if (f[2] <= 0.3496f) {
                                if (f[6] <= 0.2664f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[4] <= 0.7004f) {
                                    return 3;
                                } else {
                                    return 2;
                                }
                            }
                        }
                    }
                }
            }
        }
    } else {
        if (f[7] <= 0.9319f) {
            if (f[1] <= 0.3188f) {
                if (f[8] <= 0.2530f) {
                    if (f[1] <= 0.2314f) {
                        if (f[8] <= 0.2193f) {
                            if (f[4] <= 3.2703f) {
                                if (f[2] <= 1.5783f) {
                                    return 3;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[7] <= 0.2078f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        } else {
                            if (f[5] <= 0.5670f) {
                                return 3;
                            } else {
                                if (f[8] <= 0.2492f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        }
                    } else {
                        if (f[0] <= 0.2337f) {
                            if (f[8] <= 0.2172f) {
                                if (f[0] <= 0.2047f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                return 4;
                            }
                        } else {
                            if (f[8] <= 0.2439f) {
                                return 3;
                            } else {
                                if (f[1] <= 0.2501f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        }
                    }
                } else {
                    if (f[7] <= 0.2672f) {
                        if (f[1] <= 0.2277f) {
                            if (f[7] <= 0.2147f) {
                                if (f[1] <= 0.1538f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[4] <= 3.3601f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        } else {
                            if (f[0] <= 0.2413f) {
                                if (f[7] <= 0.2161f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[2] <= 0.4073f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        }
                    } else {
                        if (f[6] <= 0.1744f) {
                            return 3;
                        } else {
                            if (f[5] <= 0.1673f) {
                                if (f[1] <= 0.1699f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[1] <= 0.2816f) {
                                    return 4;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    }
                }
            } else {
                if (f[0] <= 0.3300f) {
                    if (f[8] <= 0.2901f) {
                        if (f[0] <= 0.2406f) {
                            if (f[8] <= 0.2189f) {
                                if (f[3] <= 4.4929f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[7] <= 0.1386f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        } else {
                            if (f[0] <= 0.2666f) {
                                if (f[8] <= 0.2637f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                return 3;
                            }
                        }
                    } else {
                        if (f[7] <= 0.2765f) {
                            if (f[0] <= 0.2435f) {
                                if (f[7] <= 0.2213f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[1] <= 0.3272f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        } else {
                            if (f[6] <= 0.2445f) {
                                if (f[4] <= 4.5867f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[5] <= 0.1862f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    }
                } else {
                    if (f[7] <= 0.3501f) {
                        if (f[2] <= 0.2509f) {
                            if (f[0] <= 1.2002f) {
                                return 3;
                            } else {
                                if (f[8] <= 0.1998f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        } else {
                            if (f[2] <= 0.2548f) {
                                if (f[2] <= 0.2532f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[0] <= 0.3340f) {
                                    return 3;
                                } else {
                                    return 3;
                                }
                            }
                        }
                    } else {
                        if (f[8] <= 0.3499f) {
                            if (f[2] <= 0.1553f) {
                                if (f[3] <= 2.1438f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[2] <= 0.3302f) {
                                    return 3;
                                } else {
                                    return 3;
                                }
                            }
                        } else {
                            if (f[1] <= 0.6031f) {
                                if (f[1] <= 0.3501f) {
                                    return 4;
                                } else {
                                    return 2;
                                }
                            } else {
                                if (f[6] <= 0.3580f) {
                                    return 3;
                                } else {
                                    return 1;
                                }
                            }
                        }
                    }
                }
            }
        } else {
            if (f[4] <= 1.6373f) {
                if (f[4] <= 0.7069f) {
                    if (f[5] <= 0.9344f) {
                        if (f[1] <= 0.4293f) {
                            return 4;
                        } else {
                            if (f[2] <= 0.4168f) {
                                return 4;
                            } else {
                                if (f[0] <= 0.3679f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        }
                    } else {
                        if (f[6] <= 0.9191f) {
                            if (f[0] <= 0.4783f) {
                                if (f[8] <= 4.5315f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[2] <= 0.5683f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            }
                        } else {
                            if (f[8] <= 0.8515f) {
                                if (f[0] <= 0.4064f) {
                                    return 4;
                                } else {
                                    return 3;
                                }
                            } else {
                                if (f[1] <= 1.8546f) {
                                    return 4;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    }
                } else {
                    if (f[2] <= 0.3525f) {
                        if (f[6] <= 0.3005f) {
                            return 3;
                        } else {
                            return 4;
                        }
                    } else {
                        if (f[6] <= 0.3608f) {
                            if (f[1] <= 0.4135f) {
                                return 4;
                            } else {
                                return 3;
                            }
                        } else {
                            if (f[1] <= 0.3413f) {
                                if (f[5] <= 0.2046f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[8] <= 0.3507f) {
                                    return 3;
                                } else {
                                    return 2;
                                }
                            }
                        }
                    }
                }
            } else {
                if (f[2] <= 0.7022f) {
                    if (f[2] <= 0.3519f) {
                        if (f[8] <= 0.2775f) {
                            return 3;
                        } else {
                            if (f[6] <= 0.1779f) {
                                return 3;
                            } else {
                                if (f[5] <= 0.1757f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        }
                    } else {
                        if (f[5] <= 0.3697f) {
                            return 3;
                        } else {
                            if (f[8] <= 0.4085f) {
                                if (f[8] <= 0.2658f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            } else {
                                if (f[6] <= 0.3298f) {
                                    return 3;
                                } else {
                                    return 2;
                                }
                            }
                        }
                    }
                } else {
                    if (f[1] <= 0.7003f) {
                        if (f[1] <= 0.3497f) {
                            if (f[6] <= 0.2870f) {
                                return 3;
                            } else {
                                if (f[5] <= 0.2455f) {
                                    return 3;
                                } else {
                                    return 4;
                                }
                            }
                        } else {
                            if (f[6] <= 0.3897f) {
                                return 3;
                            } else {
                                if (f[0] <= 0.3594f) {
                                    return 4;
                                } else {
                                    return 2;
                                }
                            }
                        }
                    } else {
                        if (f[8] <= 0.7000f) {
                            if (f[8] <= 0.3500f) {
                                return 3;
                            } else {
                                if (f[6] <= 0.3597f) {
                                    return 3;
                                } else {
                                    return 1;
                                }
                            }
                        } else {
                            if (f[0] <= 0.6979f) {
                                if (f[0] <= 0.3514f) {
                                    return 4;
                                } else {
                                    return 2;
                                }
                            } else {
                                if (f[5] <= 0.6985f) {
                                    return 1;
                                } else {
                                    return 0;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

// Auto-generated Decision Tree Regressor  (depth=6, leaves=44)
static float dt_predict_speed(const float f[9]) {
    if (f[3] <= 1.9998f) {
        if (f[3] <= 0.5992f) {
            if (f[4] <= 0.7422f) {
                if (f[4] <= 0.4504f) {
                    return 0.0000f;
                } else {
                    if (f[3] <= 0.3497f) {
                        return 0.0000f;
                    } else {
                        if (f[5] <= 0.3504f) {
                            return 0.0000f;
                        } else {
                            return 0.0307f;
                        }
                    }
                }
            } else {
                if (f[3] <= 0.3514f) {
                    return 0.0000f;
                } else {
                    if (f[2] <= 0.3524f) {
                        if (f[2] <= 0.3506f) {
                            return 0.0000f;
                        } else {
                            return 0.0375f;
                        }
                    } else {
                        if (f[1] <= 0.3551f) {
                            return 0.0007f;
                        } else {
                            return 0.1476f;
                        }
                    }
                }
            }
        } else {
            if (f[7] <= 0.8265f) {
                if (f[7] <= 0.3504f) {
                    return 0.0000f;
                } else {
                    if (f[8] <= 0.3528f) {
                        if (f[8] <= 0.3510f) {
                            return 0.0000f;
                        } else {
                            return 0.0231f;
                        }
                    } else {
                        if (f[1] <= 0.3503f) {
                            return 0.0000f;
                        } else {
                            return 0.1427f;
                        }
                    }
                }
            } else {
                if (f[1] <= 0.7986f) {
                    if (f[1] <= 0.3523f) {
                        return 0.0000f;
                    } else {
                        if (f[2] <= 0.3506f) {
                            return 0.0000f;
                        } else {
                            return 0.1573f;
                        }
                    }
                } else {
                    if (f[4] <= 1.1006f) {
                        if (f[4] <= 0.7013f) {
                            return 0.0144f;
                        } else {
                            return 0.1563f;
                        }
                    } else {
                        if (f[0] <= 0.3451f) {
                            return 0.0000f;
                        } else {
                            return 0.3951f;
                        }
                    }
                }
            }
        }
    } else {
        if (f[7] <= 1.8876f) {
            if (f[8] <= 0.8026f) {
                if (f[8] <= 0.3501f) {
                    return 0.0000f;
                } else {
                    if (f[7] <= 0.3500f) {
                        return 0.0000f;
                    } else {
                        if (f[6] <= 0.3504f) {
                            return 0.0000f;
                        } else {
                            return 0.1348f;
                        }
                    }
                }
            } else {
                if (f[7] <= 0.3511f) {
                    return 0.0000f;
                } else {
                    if (f[4] <= 1.1928f) {
                        if (f[4] <= 0.6982f) {
                            return 0.0147f;
                        } else {
                            return 0.1546f;
                        }
                    } else {
                        if (f[5] <= 0.3456f) {
                            return 0.0000f;
                        } else {
                            return 0.3675f;
                        }
                    }
                }
            }
        } else {
            if (f[4] <= 1.6373f) {
                if (f[4] <= 1.1098f) {
                    if (f[4] <= 0.7098f) {
                        if (f[4] <= 0.4477f) {
                            return 0.0000f;
                        } else {
                            return 0.0376f;
                        }
                    } else {
                        if (f[6] <= 0.3611f) {
                            return 0.0000f;
                        } else {
                            return 0.1502f;
                        }
                    }
                } else {
                    if (f[2] <= 0.3373f) {
                        return 0.0000f;
                    } else {
                        if (f[6] <= 0.3465f) {
                            return 0.0000f;
                        } else {
                            return 0.3268f;
                        }
                    }
                }
            } else {
                if (f[2] <= 1.9444f) {
                    if (f[2] <= 0.3554f) {
                        return 0.0000f;
                    } else {
                        if (f[1] <= 0.4082f) {
                            return 0.0086f;
                        } else {
                            return 0.3862f;
                        }
                    }
                } else {
                    if (f[0] <= 1.9995f) {
                        if (f[0] <= 0.3520f) {
                            return 0.0000f;
                        } else {
                            return 0.4209f;
                        }
                    } else {
                        if (f[8] <= 1.8714f) {
                            return 0.3620f;
                        } else {
                            return 0.6993f;
                        }
                    }
                }
            }
        }
    }
}

#endif /* DECISION_TREE_MODEL_H */
