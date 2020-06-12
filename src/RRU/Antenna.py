class Antenna:
    RRU_NONE = "000000000"

    @staticmethod
    def not_none(s_value):
        if s_value == Antenna.RRU_NONE:
            return ""
        else:
            return s_value

    def __init__(self):
        self.tddSlot = Antenna.RRU_NONE
        self.tddSlot2Set = Antenna.RRU_NONE
        self.tddSlotOutDated = True

        self.sSlot = Antenna.RRU_NONE
        self.sSlot2Set = Antenna.RRU_NONE
        self.sSlotOutDated = True

        self.txAttenuation = Antenna.RRU_NONE
        self.txAttenuation2Set = Antenna.RRU_NONE
        self.txAttenuationOutDated = True
        self.rxGainAttenuation = Antenna.RRU_NONE
        self.rxGainAttenuation2Set = Antenna.RRU_NONE
        self.rxGainAttenuationOutDated = True

        self.dlFrameOffset = Antenna.RRU_NONE
        self.dlFrameOffset2Set = Antenna.RRU_NONE
        self.dlFrameOffsetOutDated = True
        self.ulFrameOffset = Antenna.RRU_NONE
        self.ulFrameOffset2Set = Antenna.RRU_NONE
        self.ulFrameOffsetOutDated = True

        self.linkDelay = Antenna.RRU_NONE
        self.linkDelay2Set = Antenna.RRU_NONE
        self.linkDelayOutDated = True
