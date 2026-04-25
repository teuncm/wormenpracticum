Device = {}


def makeworm():
    # First 4 bits of wselect are stim1 location, last 4 bits are stim2 location.
    # Set initial nulcode: bits 4–7 high (16 + 32 + 64 + 128 = 240)
    nulcode = 16 + 32 + 64 + 128
    wselect = 0

    if Device['stim1'] > 1:
        wselect += (Device['stim1'] - 1)
        nulcode -= 32  # clear bit 5

    if Device['stim2'] > 1:
        wselect += (Device['stim2'] - 1) * 16
        nulcode -= 64  # clear bit 6

    Device[1]['val1'] = round(wselect)
    Device[1]['val3'] = round(nulcode)


