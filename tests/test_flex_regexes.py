# stdlib imports
import unittest
import itertools
import os


# local imports
from capgains.flex import regexes


def setUpModule():
    """ Load corporate action description data """
    global corpActDescriptions
    path = os.path.join(os.path.dirname(__file__), "data", "corpact_descriptions.txt")
    with open(path) as f:
        corpActDescriptions = f.readlines()


class CorpActReTestCase(unittest.TestCase):
    regex = regexes.corpActRE

    @property
    def descriptions(self):
        # Wrap in property because corpActDescriptions hasn't been defined yet
        # at class creation time
        return corpActDescriptions

    def runRegex(self):
        return [self.regex.match(desc) for desc in self.descriptions]

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            split = desc.split("(")
            tail = split[-1].rstrip(")")
            extracted = [t for t in tail.split(",")]
            cusip = extracted.pop().strip().rstrip(")")
            ticker = extracted.pop(0).strip()
            if ticker.startswith("20"):
                ticker = ticker[14:]
            name = ",".join(extracted).strip()
            memo = "(".join(split[:-1]).strip()
            match = matches[i]
            if match is None:
                raise ValueError(desc)
            self.assertEqual(ticker, match.group("ticker"))
            self.assertEqual(name, match.group("secname"))
            self.assertEqual(cusip, match.group("cusip"))
            self.assertEqual(memo, match.group("memo"))


class ChangeSecurityReTestCase(CorpActReTestCase):
    memoSignature = "CUSIP/ISIN CHANGE"
    regex = regexes.changeSecurityRE

    @property
    def descriptions(self):
        return [
            regexes.corpActRE.match(desc).group("memo").strip()
            for desc in corpActDescriptions
            if self.memoSignature in desc
        ]

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )[:-1]
            self.assertEqual(len(split), 4)
            match = matches[i]
            tickerFrom, isinFrom, boilerplate, isinTo0 = split
            self.assertEqual(tickerFrom, match.group("tickerFrom"))
            self.assertEqual(isinFrom, match.group("isinFrom"))
            self.assertEqual(isinTo0, match.group("isinTo0"))


class OversubscribeReTestCase(ChangeSecurityReTestCase):
    memoSignature = "OVER SUBSCRIBE "
    regex = regexes.oversubscribeRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            self.assertEqual(len(split), 3)
            ticker, isin, priceCurrency = split
            ticker = ticker[
                ticker.index(self.memoSignature) + len(self.memoSignature) :
            ]
            priceCurrency = priceCurrency.strip().split()
            self.assertEqual(len(priceCurrency), 3)
            price, currency = priceCurrency[1:]

            match = matches[i]
            self.assertEqual(ticker, match.group("ticker"))
            self.assertEqual(isin, match.group("isin"))
            self.assertEqual(price, match.group("price"))
            self.assertEqual(currency, match.group("currency"))


class RightsIssueReTestCase(ChangeSecurityReTestCase):
    memoSignature = "SUBSCRIBABLE RIGHTS ISSUE"
    regex = regexes.rightsIssueRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            self.assertEqual(len(split), 3)
            tickerFrom, isinFrom, ratio = split
            ratio = ratio.strip().split()
            self.assertEqual(len(ratio), 6)
            self.assertEqual(ratio[4], "FOR")
            numerator = ratio[3]
            denominator = ratio[5]
            match = matches[i]
            self.assertEqual(tickerFrom, match.group("tickerFrom"))
            self.assertEqual(isinFrom, match.group("isinFrom"))
            self.assertEqual(numerator, match.group("numerator0"))
            self.assertEqual(denominator, match.group("denominator0"))


class SplitReTestCase(ChangeSecurityReTestCase):
    memoSignature = "SPLIT"
    regex = regexes.splitRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            self.assertEqual(len(split), 3)
            tickerFrom, isinFrom, ratio = split
            ratio = ratio.strip().split()
            self.assertEqual(len(ratio), 4)
            self.assertEqual(ratio[2], "FOR")
            numerator0 = ratio[1]
            denominator0 = ratio[3]
            match = matches[i]
            self.assertEqual(tickerFrom, match.group("tickerFrom"))
            self.assertEqual(isinFrom, match.group("isinFrom"))
            self.assertEqual(numerator0, match.group("numerator0"))
            self.assertEqual(denominator0, match.group("denominator0"))


class StockDividendReTestCase(ChangeSecurityReTestCase):
    memoSignature = "STOCK DIVIDEND"
    regex = regexes.stockDividendRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            self.assertEqual(len(split), 3)
            tickerFrom, isinFrom, ratio = split
            ratio = ratio.strip().split()
            self.assertEqual(len(ratio), 5)
            self.assertEqual(ratio[3], "FOR")
            numerator0 = ratio[2]
            denominator0 = ratio[4]
            match = matches[i]
            self.assertEqual(tickerFrom, match.group("tickerFrom"))
            self.assertEqual(isinFrom, match.group("isinFrom"))
            self.assertEqual(numerator0, match.group("numerator0"))
            self.assertEqual(denominator0, match.group("denominator0"))


class SpinoffReTestCase(ChangeSecurityReTestCase):
    memoSignature = "SPINOFF "
    regex = regexes.spinoffRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            self.assertEqual(len(split), 3)
            tickerFrom, isinFrom, ratios = split
            ratios = [r.split()[-3:] for r in ratios.split(",")]
            match = matches[i]

            ratio = ratios[0]
            numerator0, FOR, denominator0 = ratio
            self.assertEqual(FOR, "FOR")
            self.assertEqual(tickerFrom, match.group("tickerFrom"))
            self.assertEqual(isinFrom, match.group("isinFrom"))
            self.assertEqual(numerator0, match.group("numerator0"))
            self.assertEqual(denominator0, match.group("denominator0"))

            if len(ratios) > 1:
                self.assertEqual(len(ratios), 2)
                ratio = ratios[1]
                numerator1, FOR, denominator1 = ratio
                self.assertEqual(FOR, "FOR")
                self.assertEqual(numerator1, match.group("numerator1"))
                self.assertEqual(denominator1, match.group("denominator1"))


class SubscribeReTestCase(ChangeSecurityReTestCase):
    memoSignature = "SUBSCRIBES TO"
    regex = regexes.subscribeRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            match = matches[i]
            self.assertEqual(split[0], match.group("tickerFrom"))
            self.assertEqual(split[1], match.group("isinFrom"))


class CashMergerReTestCase(ChangeSecurityReTestCase):
    memoSignature = "PER SHARE"
    regex = regexes.cashMergerRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            tickerFrom, isinFrom, *terms = split
            terms = terms[-1].split("FOR ")[-1].split()
            self.assertEqual(len(terms), 4)
            self.assertEqual(terms[2:], ["PER", "SHARE"])
            currency, price = terms[:2]

            match = matches[i]
            self.assertEqual(tickerFrom, match.group("tickerFrom"))
            self.assertEqual(isinFrom, match.group("isinFrom"))
            self.assertEqual(currency, match.group("currency"))
            self.assertEqual(price, match.group("price"))


class KindMergerReTestCase(ChangeSecurityReTestCase):
    memoSignature = "WITH"
    regex = regexes.kindMergerRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            match = matches[i]

            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            tickerFrom = split[0]
            isinFrom = split[1]

            self.assertEqual(tickerFrom, match.group("tickerFrom"))
            self.assertEqual(isinFrom, match.group("isinFrom"))

            terms = split[-1].replace("MERGED", "").replace("WITH", "").strip()
            terms = [t.split() for t in terms.split(",")]
            term = terms[0]
            self.assertEqual(len(term), 4)
            tickerTo0, numerator0, FOR, denominator0 = term

            self.assertEqual(tickerTo0, match.group("tickerTo0"))
            self.assertEqual(numerator0, match.group("numerator0"))
            self.assertEqual(FOR, "FOR")
            self.assertEqual(denominator0, match.group("denominator0"))

            if len(terms) > 1:
                self.assertEqual(len(terms), 2)
                term = terms[1]

                if len(term) > 1:
                    self.assertEqual(len(term), 4)
                    tickerTo1, numerator1, FOR, denominator1 = term
                    self.assertEqual(term[0], match.group("tickerTo1"))
                    self.assertEqual(numerator1, match.group("numerator1"))
                    self.assertEqual(FOR, "FOR")
                    self.assertEqual(denominator1, match.group("denominator1"))


class CashAndKindMergerReTestCase(ChangeSecurityReTestCase):
    memoSignature = "CASH and STOCK MERGER"
    regex = regexes.cashAndKindMergerRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            match = matches[i]

            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            self.assertEqual(len(split), 5)
            tickerFrom = split[0]
            isinFrom = split[1]
            self.assertEqual(tickerFrom, match.group("tickerFrom"))
            self.assertEqual(isinFrom, match.group("isinFrom"))

            terms = split[-1].strip().split(" AND ")[0].split()
            self.assertEqual(len(terms), 4)
            tickerTo0, numerator0, FOR, denominator0 = terms

            self.assertEqual(tickerTo0, match.group("tickerTo0"))
            self.assertEqual(numerator0, match.group("numerator0"))
            self.assertEqual(FOR, "FOR")
            self.assertEqual(denominator0, match.group("denominator0"))


class TenderReTestCase(ChangeSecurityReTestCase):
    memoSignature = "TENDERED TO"
    regex = regexes.tenderRE

    def testRegex(self):
        matches = self.runRegex()
        self.assertEqual(len(matches), len(self.descriptions))
        for i, desc in enumerate(self.descriptions):
            match = matches[i]

            split = list(
                itertools.chain.from_iterable([m.split(")") for m in desc.split("(")])
            )
            self.assertEqual(split[0], match.group("tickerFrom"))
            self.assertEqual(split[1], match.group("isinFrom"))
            if split[-1]:
                terms = split[-1].replace("TENDERED TO", "")
            else:
                terms = split[-2]
            terms = terms.strip().split()
            self.assertEqual(terms[0], match.group("tickerTo0"))
            if len(terms) > 1:
                tickerTo0, numerator0, FOR, denominator0 = terms
                self.assertEqual(numerator0, match.group("numerator0"))
                self.assertEqual(FOR, "FOR")
                self.assertEqual(denominator0, match.group("denominator0"))


# corpActDescriptions = [
# "MFCAF(P64605101) STOCK DIVIDEND 1 FOR 11 (MFCAF, MASS FINANCIAL CORP-CL A, P64605101)",
# "MFCAF(P64605101) TENDERED TO (MFCAF.TEN) (MFCAF, MASS FINANCIAL CORP-CL A, BBP646051012)",
# "MFCAF(P64605101) TENDERED TO (MFCAF.TEN) (MFCAF.TEN, MASS FINANCIAL CORP-CL A - TENDER, BBP649900165)",
# "MFCAF.TEN(P64990016) MERGED WITH TTT 1 FOR 1 (MFCAF.TEN, MASS FINANCIAL CORP-CL A - TENDER, BBP649900165)",
# "MFCAF.TEN(P64990016) MERGED WITH TTT 1 FOR 1 (TTT, TERRA NOVA ROYALTY CORP, 88102D103)",
# "WAHUQ(US9393228484) TENDERED TO WAHUQ.EXC 1 FOR 1 (WAHUQ, WASHINGTON MUTUAL UT, 939322848)",
# "WAHUQ(US9393228484) TENDERED TO WAHUQ.EXC 1 FOR 1 (WAHUQ.EXC, WASHINGTON MUTUAL UT - EXCHANGE ELECTION, 939EXC988)",
# "EDCI(US2683151086) CUSIP/ISIN CHANGE TO (US2683152076) (EDCI.OLD, EDCI HOLDINGS INC, 268315108)",
# "EDCI(US2683151086) CUSIP/ISIN CHANGE TO (US2683152076) (EDCID, EDCI HOLDINGS INC, 268315207)",
# "MOSH(US5906501078) ACQUIRED FOR USD 0.012984 PER SHARE (MOSH, MESA OFFSHORE TR UNIT, 590650107)",
# "TTT(CA88102D1033) SPINOFF KWG.SPN 1 FOR 10 (KWG.SPN, KHD HUMBOLDT WEDAG INTERNATIONAL AG, 482462991)",
# "KWG.SPN(CA4824629915) MERGED(Acquisition)  WITH KWG 1 FOR 1 (KWG, KHD HUMBOLDT WEDAG INTERNATION, DE0006578008)",
# "KWG.SPN(CA4824629915) MERGED(Acquisition)  WITH KWG 1 FOR 1 (KWG.SPN, KHD HUMBOLDT WEDAG INTERNATIONAL AG, 482462991)",
# "WAHUQ.EXC(US939EXC9881) MERGED(Voluntary Offer Allocation)  WITH WAHUQ 1 FOR 1 (WAHUQ, WASHINGTON MUTUAL UT, 939322848)",
# "WAHUQ.EXC(US939EXC9881) MERGED(Voluntary Offer Allocation)  WITH WAHUQ 1 FOR 1 (WAHUQ.EXC, WASHINGTON MUTUAL UT - EXCHANGE ELECTION, 939EXC988)",
# "FMTI(CA3451551053) CUSIP/ISIN CHANGE TO (CA30252D1033) (FMTI.OLD, FORBES MEDI-TECH INC, 345155105)",
# "FMTI(CA3451551053) CUSIP/ISIN CHANGE TO (CA30252D1033) (FMTIF, FMI HOLDINGS LTD, 30252D103)",
# "CNVR(US2119191052) MERGED(Liquidation)  FOR USD 0.04700000 PER SHARE (CNVR, CONVERA CORPORATION, 211919105)",
# "TNFG(US8726061083) MERGED(Liquidation)  FOR USD 0.10300000 PER SHARE (TNFG, TNFG CORP, 872606108)",
# "TTT(CA88102D1033) CUSIP/ISIN CHANGE TO (CA55278T1057) (MIL, MFC INDUSTRIAL LTD, 55278T105)",
# "TTT(CA88102D1033) CUSIP/ISIN CHANGE TO (CA55278T1057) (TTT.OLD, MFC INDUSTRIAL LTD, 88102D103)",
# "NILSY(US46626D1081) TENDERED TO NILSY.TEN 1 FOR 1 (NILSY, MMC NORILSK NICKEL JSC-ADR, 46626D108)",
# "NILSY(US46626D1081) TENDERED TO NILSY.TEN 1 FOR 1 (NILSY.TEN, MMC NORILSK NICKEL JSC-ADR - TENDER, 466992534)",
# "NILSY.TEN(466992534) MERGED(Voluntary Offer Allocation)  FOR USD 30.60000000 PER SHARE (NILSY.TEN, MMC NORILSK NICKEL JSC-ADR - TENDER, 466992534)",
# "DIMEQ(US25429Q1105) TENDERED TO US254EXC9938 1 FOR 1 (DIMEQ, DIME BANCORP WT, 25429Q110)",
# "DIMEQ(US25429Q1105) TENDERED TO US254EXC9938 1 FOR 1 (DIMEQ.EXC, DIME BANCORP WT - TENDER - EXCHANGE, 254EXC993)",
# "DIMEQ.TMP(US254TMP9913) CASH and STOCK MERGER (Voluntary Offer Allocation) WMIH 1146667 FOR 10000000 (DIME.ESCR, DIME BANCORP WT - ESCROW SHARES, 254ESC890)",
# "DIMEQ.EXC(US254EXC9938) TENDERED TO US254TMP9913 1 FOR 1 (DIMEQ.EXC, DIME BANCORP WT - TENDER - EXCHANGE, 254EXC993)",
# "DIMEQ.EXC(US254EXC9938) TENDERED TO US254TMP9913 1 FOR 1 (DIMEQ.TMP, DIME BANCORP WT - TEMP, 254TMP991)",
# "DIMEQ.TMP(US254TMP9913) CASH and STOCK MERGER (Voluntary Offer Allocation) WMIH 1146667 FOR 10000000 (DIMEQ.TMP, DIME BANCORP WT - TEMP, 254TMP991)",
# "DIMEQ.TMP(US254TMP9913) CASH and STOCK MERGER (Voluntary Offer Allocation) WMIH 1146667 FOR 10000000 (WMIH, WMI HOLDINGS CORP, 92936P100)",
# "ELAN(US28413U2042) TENDERED TO US28413TEMP2 1 FOR 1 (ELAN, ELANDIA INTERNATIONAL INC, 28413U204)",
# "ELAN.TEMP(US28413TEMP2) MERGED(Acquisition)  WITH US284CNT9952 1 FOR 10000 (ELAN.CNT, ELANDIA INTERNATIONAL INC - CONTRA, 284CNT995)",
# "ELAN(US28413U2042) TENDERED TO US28413TEMP2 1 FOR 1 (ELAN.TEMP, ELANDIA INTERNATIONAL INC - TEMP, 28413TEMP)",
# "ELAN.TEMP(US28413TEMP2) MERGED(Acquisition)  WITH US284CNT9952 1 FOR 10000 (ELAN.TEMP, ELANDIA INTERNATIONAL INC - TEMP, 28413TEMP)",
# "ELAN.TEMP(US28413TEMP2) MERGED(Acquisition)  WITH US284CNT9952 1 FOR 10000 (ELAN.CNT, ELANDIA INTERNATIONAL INC - CONTRA, 284CNT995)",
# "ELAN.TEMP(US28413TEMP2) MERGED(Acquisition)  WITH US284CNT9952 1 FOR 10000 (ELAN.CNT, ELANDIA INTERNATIONAL INC - CONTRA, 284CNT995)",
# "ELAN.TEMP(US28413TEMP2) MERGED(Acquisition)  WITH US284CNT9952 1 FOR 10000 (ELAN.TEMP, ELANDIA INTERNATIONAL INC - TEMP, 28413TEMP)",
# "ELAN.TEMP(US28413TEMP2) MERGED(Acquisition)  WITH US284CNT9952 1 FOR 10000 (ELAN.TEMP, ELANDIA INTERNATIONAL INC - TEMP, 28413TEMP)",
# "JAKK(US47012E1064) TENDERED TO US4709910271 1 FOR 1 (JAKK, JAKKS PACIFIC INC, 47012E106)",
# "JAKK(US47012E1064) TENDERED TO US4709910271 1 FOR 1 (JAKK.TEN, JAKKS PACIFIC INC - TENDER, 470991027)",
# "JAKK(US47012E1064) TENDERED TO US4709910271 1 FOR 1 (JAKK, JAKKS PACIFIC INC, 47012E106)",
# "JAKK(US47012E1064) TENDERED TO US4709910271 1 FOR 1 (JAKK.TEN, JAKKS PACIFIC INC - TENDER, 470991027)",
# "JAKK.TEN(US4709910271) MERGED(Voluntary Offer Allocation)  FOR USD 20.00000000 PER SHARE (JAKK.TEN, JAKKS PACIFIC INC - TENDER, 470991027)",
# "JAKK.TEN(US4709910271) MERGED(Voluntary Offer Allocation)  FOR USD 20.00000000 PER SHARE (JAKK.TEN, JAKKS PACIFIC INC - TENDER, 470991027)",
# "VXX(US06740C2614) SPLIT 1 FOR 4 (VXX, IPATH S&amp;P 500 VIX S/T FU ETN, 06740C188)",
# "VXX(US06740C2614) SPLIT 1 FOR 4 (VXX.OLD, IPATH S&amp;P 500 VIX S/T FU ETN, 06740C261)",
# "(CA30252D1033) DELISTED (FMTIF, FMI HOLDINGS LTD, 30252D103)",
# "KSW(US48268R1068) TENDERED TO US4829928492 1 FOR 1 (KSW, KSW INC, 48268R106)",
# "KSW(US48268R1068) TENDERED TO US4829928492 1 FOR 1 (KSW.TEN, KSW INC - TENDER, 482992849)",
# "KSW.TEN(US4829928492) MERGED(Voluntary Offer Allocation)  FOR USD 5.00000000 PER SHARE (KSW.TEN, KSW INC - TENDER, 482992849)",
# "(US254ESC8903) DELISTED (DIME.ESCR, DIME BANCORP WT - ESCROW SHARES, 254ESC890)",
# "LUK(US5272881047) SPINOFF  1 FOR 10 (CWGL, CRIMSON WINE GROUP LTD-WI, 22662X100)",
# "VLCY.ESC(US929ESC9600) MERGED(Liquidation)  FOR USD 0.25658627 PER SHARE (VLCY.ESC, VOYAGER LEARNING ESCROW FROM VOLUNTARY ELECTION, 929ESC960)",
# "VLCY.ESC(US929ESC9600) MERGED(Liquidation)  FOR USD 0.25658627 PER SHARE (VLCY.ESC, VOYAGER LEARNING ESCROW FROM VOLUNTARY ELECTION, 929ESC960)",
# "CNVR(US2119191052) SPINOFF  378372 FOR 10000000000 (CNVR.SPO, CONVERA CORPORATION - SPINOFF, 92534R995)",
# "CNVR.SPO(US92534R9950) MERGED(Acquisition)  WITH US92534R1023 1 FOR 1 (CNVR.SPO, CONVERA CORPORATION - SPINOFF, 92534R995)",
# "CNVR.SPO(US92534R9950) MERGED(Acquisition)  WITH US92534R1023 1 FOR 1 (VSW, VERTICAL SEARCH WORKS, INC. - PRIVATE COMPANY, 92534R102)",
# "AMP.RSTD(135893865) MERGED(Acquisition)  WITH AMP.REST 1 FOR 1 (AMP.REST, AMPER SA - RESTRICTED, ES010RSTD531)",
# "AMP.RSTD(135893865) MERGED(Acquisition)  WITH AMP.REST 1 FOR 1 (AMP.REST, AMPER SA - RESTRICTED, ES010RSTD531)",
# "AMP.REST(ES010RSTD531) SUBSCRIBABLE RIGHTS ISSUE  1 FOR 1 (AMP.D, AMPER SA - RIGHTS 131101, ES0609260916)",
# "AMP.REST(ES010RSTD531) MERGED(Acquisition)  WITH ES0109260531 1 FOR 1 (AMP, AMPER SA, ES0109260531)",
# "AMP.REST(ES010RSTD531) MERGED(Acquisition)  WITH ES0109260531 1 FOR 1 (AMP.REST, AMPER SA - RESTRICTED, ES010RSTD531)",
# "AMP.RSTD(135893865) MERGED(Acquisition)  WITH AMP.REST 1 FOR 1 (AMP.RSTD, AMPER SA - RESTRICTED, ES010RSTD531)",
# "ELAN.TEMP(US28413TEMP2) SPINOFF  1265 FOR 10000 (AMP.RSTD, AMPER SA - RESTRICTED, ES010RSTD531)",
# "(US284CNT9952) DELISTED (ELAN.CNT, ELANDIA INTERNATIONAL INC - CONTRA, 284CNT995)",
# "AMP.RSTD(135893865) MERGED(Acquisition)  WITH AMP.REST 1 FOR 1 (AMP.RSTD, AMPER SA - RESTRICTED, ES010RSTD531)",
# "(ES0609260916) DELISTED (AMP.D, AMPER SA - RTS, ES0609260916)",
# "VXX(US06740C1889) SPLIT 1 FOR 4 (VXX, IPATH S&amp;P 500 VIX S/T FU ETN, 06742E711)",
# "VXX(US06740C1889) SPLIT 1 FOR 4 (VXX.OLD, IPATH S&amp;P 500 VIX S/T FU ETN, 06740C188)",
# "(US6533511068) DELISTED (NEXC, NEXCEN BRANDS INC, 653351106)",
# "ADGI(US0191181082) CASH and STOCK MERGER (Liquidation) US019ESC8057 1 FOR 1 AND USD 5.11000000 (ADGI, ALLIED DEFENSE GROUP INC/THE, 019118108)",
# "ADGI(US0191181082) CASH and STOCK MERGER (Liquidation) US019ESC8057 1 FOR 1 AND USD 5.11000000 (ADGI.ESC, ALLIED DEFENSE GROUP INC/THE - CONTRA, 019ESC805)",
# "GYRO(US4038201038) SPINOFF  1 FOR 1 (GYRO.NOTE, GYRODYNE CO OF AMERICA INC - 10.89 NON-TRANSFERABLE NOTES, 403NOTE03)",
# "GYRO(US4038201038) SPINOFF  1 FOR 1 (GYRO.NTS, GYRODYNE CO OF AMERICA INC - 20.70 INTERESTS, 4038NOTE3)",
# "PATH(US67059M1009) TENDERED TO US670WAV1099 1 FOR 1 (PATH, NUPATHE INC, 67059M100)",
# "PATH(US67059M1009) TENDERED TO US670WAV1099 1 FOR 1 (PATH.WDR, NUPATHE INC - WAIVE DISSENTERS RIGHTS, 670WAV109)",
# "PATH.WDR(US670WAV1099) CASH and STOCK MERGER (Voluntary Offer Allocation) US881CNT9926 1 FOR 1 AND U (PATH.CVR1, NUPATHE INC - CONTINGENT VALUE RIGHT, 881CNT992)",
# "PATH.WDR(US670WAV1099) CASH and STOCK MERGER (Voluntary Offer Allocation) US881CNT9926 1 FOR 1 AND U (PATH.WDR, NUPATHE INC - WAIVE DISSENTERS RIGHTS, 670WAV109)",
# "WMI SECON(US92936PAB67) STOCK DIVIDEND 325 FOR 10000 (WMI SECON, WMI HLDGS CORP 13% SECOND LIEN NOTE 03/16/2030, 92936PAB6)",
# "WMI FIRST(US92936PAA84) TENDERED TO US92CALLAA84 1 FOR 1 (WMI FIRST, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030, 92936PAA8)",
# "WMI FIRST(US92936PAA84) TENDERED TO US92CALLAA84 1 FOR 1 (WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CALL, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CALL, 92CALLAA8)",
# "WMI FIRST(US92936PAA84) TENDERED TO US929CALLA81 1 FOR 1 (WMI FIRST, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030, 92936PAA8)",
# "WMI FIRST(US92936PAA84) TENDERED TO US929CALLA81 1 FOR 1 (WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CAL, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CAL, 929CALLA8)",
# "CHTP(US1634281059) MERGED(Mandatory Offer Allocation)  FOR USD 6.44000000 PER SHARE (CHTP, CHELSEA THERAPEUTICS INTERNA, 163428105)",
# "CHTP(US1634281059) SPINOFF  1 FOR 1 (CHTP.ESC, CHELSEA THERAPEUTICS INTERNA - ESCROW, 163ESC908)",
# "OSGIQ(US6903681053) TENDERED TO US690USS9905 1 FOR 1 (OSGIQ, OVERSEAS SHIPHOLDING GROUP, 690368105)",
# "OSGIQ(US6903681053) TENDERED TO US690USS9905 1 FOR 1 (OSGIQ.EX, OVERSEAS SHIPHOLDING GROUP - RTS EX U.S. HOLDER, 690USS990)",
# "OSGIQ.RT (US690USS9RT6) SUBSCRIBES TO () (OSG.R.EX1, OVERSEAS SHIPHOLDING GROUP - RTS EX US HOLDER, 690USS9EX)",
# "OSGIQ.EX(US690USS9905) SUBSCRIBABLE RIGHTS ISSUE  1 FOR 1 (OSGIQ.RT, OVERSEAS SHIPHOLDING GROUP - RIGHTS US HOLDER, 690USS9RT)",
# "OSGIQ.RT (US690USS9RT6) SUBSCRIBES TO () (OSGIQ.RT, OVERSEAS SHIPHOLDING GROUP - RIGHTS US HOLDER, 690USS9RT)",
# "929CALLA8(US929CALLA81) MERGED(Full Call)  FOR USD 1.00000000 PER SHARE (WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CAL, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CAL, 929CALLA8)",
# "92CALLAA8(US92CALLAA84) MERGED(Full Call)  FOR USD 1.00000000 PER SHARE (WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CALL, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CALL, 92CALLAA8)",
# "GYRO.NOTE(US403NOTE034) SPINOFF  204187 FOR 1000000 (GYRO.NTS2, GYRODYNE CO OF AMERICA INC - GLOBAL DIVIDEND NOTE - PIK, 403PIK103)",
# "OSG.R.EX1(US690USS9EX6) MERGED(Voluntary Offer Allocation)  WITH US69036R2022 1 FOR 1 (OSG.R.EX1, OVERSEAS SHIPHOLDING GROUP - RTS EX US HOLDER, 690USS9EX)",
# "OSG.R.EX1(US690USS9EX6) MERGED(Voluntary Offer Allocation)  WITH US69036R2022 1 FOR 1 (OSGIQ.A, OVERSEAS SHIPHOLDING GROUP CLASS A, 69036R202)",
# "(US690USS9905) DELISTED (OSGIQ.EX, OVERSEAS SHIPHOLDING GROUP - RTS EX U.S. HOLDER, 690USS990)",
# "WMI SECON(US92936PAB67) STOCK DIVIDEND 325 FOR 10000 (WMI SECON, WMI HLDGS CORP 13% SECOND LIEN NOTE 03/16/2030, 92936PAB6)",
# "WMI FIRST(US92936PAA84) STOCK DIVIDEND 325 FOR 10000 (WMI FIRST, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030, 92936PAA8)",
# "SHLD.OS2(US8129911OS0) MERGED(Voluntary Offer Allocation)  WITH SHLDW 175994 FOR 10000,US812350AF31 (SHLD 8 12/15/19, SHLD 8 12/15/19, 812350AF3)",
# "SHLD.EX2(US8129916933) MERGED(Voluntary Offer Allocation)  WITH SHLDW 175994 FOR 10000,US812350AF31 (SHLD 8 12/15/19, SHLD 8 12/15/19, 812350AF3)",
# "SHLDZ (US8123501483) SUBSCRIBES TO () (SHLD.EX2, SEARS HOLDINGS CORP - RIGHTS SUBSCRIPTION, 812991693)",
# "OVER SUBSCRIBE SHLD.OS2 (US8129911OS0) AT 500.00 USD (SHLD.OS2, SEARS HOLDINGS CORP - RIGHTS OVERSUBSCRIPTION, 8129911OS)",
# "SHLDZ (US8123501483) SUBSCRIBES TO () (SHLDZ, SEARS HOLDINGS CORP - RTS, 812350148)",
# "SHLD.EX2(US8129916933) MERGED(Voluntary Offer Allocation)  WITH SHLDW 175994 FOR 10000,US812350AF31 (SHLD.EX2, SEARS HOLDINGS CORP - RIGHTS SUBSCRIPTION, 812991693)",
# "SHLD.OS2(US8129911OS0) MERGED(Voluntary Offer Allocation)  WITH SHLDW 175994 FOR 10000,US812350AF31 (SHLD.OS2, SEARS HOLDINGS CORP - RIGHTS OVERSUBSCRIPTION, 8129911OS)",
# "OVER SUBSCRIBE SHLD.OS2 (US8129911OS0) AT 500.00 USD (SHLD.OS2, SEARS HOLDINGS CORP - RIGHTS OVERSUBSCRIPTION, 8129911OS)",
# "SHLD.OS2(US8129911OS0) MERGED(Voluntary Offer Allocation)  WITH SHLDW 175994 FOR 10000,US812350AF31 (SHLDW, SHLD 15DEC19 28.41 C, 812350155)",
# "SHLD.EX2(US8129916933) MERGED(Voluntary Offer Allocation)  WITH SHLDW 175994 FOR 10000,US812350AF31 (SHLDW, SHLD 15DEC19 28.41 C, 812350155)",
# "WMI SECON(US92936PAB67) STOCK DIVIDEND 13 FOR 400 (WMI SECON, WMI HLDGS CORP 13% SECOND LIEN NOTE 03/16/2030, 92936PAB6)",
# "WMI FIRST(US92936PAA84) TENDERED TO US9293CALL84 1 FOR 1 (WMI FIRST, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030, 92936PAA8)",
# "WMI FIRST(US92936PAA84) TENDERED TO US9293CALL84 1 FOR 1 (WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CALL, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CALL, 9293CALL8)",
# "ADGI.ESC(US019ESC8057) MERGED(Liquidation)  FOR USD 0.10000000 PER SHARE (ADGI.ESC, ALLIED DEFENSE GROUP INC/THE - CONTRA, 019ESC805)",
# "9293CALL8(US9293CALL84) MERGED(Partial Call)  FOR USD 1.00000000 PER SHARE (WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CALL, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030 - PARTIAL CALL, 9293CALL8)",
# "SGGH(US82670K1025) CUSIP/ISIN CHANGE TO (US82670K1280) (SGGH.OLD, SIGNATURE GROUP HOLDINGS INC, 82670K102)",
# "SGGH(US82670K1025) CUSIP/ISIN CHANGE TO (US82670K1280) (SGGHU, SIGNATURE GROUP HOLDINGS INC, 82670K128)",
# "GYRO.NOTE(US403NOTE034) SPLIT 1089 FOR 100 (20140822144148GYRO.NOTE, GYRODYNE CO OF AMERICA INC - 10.89 NON-TRANSFERABLE NOTES, 403NOTE03)",
# "GYRO.NOTE(US403NOTE034) SPINOFF  1 FOR 40 (GYRO.NTS2, GYRODYNE CO OF AMERICA INC - GLOBAL DIVIDEND NOTE - PIK, 403PIK103)",
# "SWY(US7865142084) SPINOFF SWY.CVR1 1 FOR 1, 1 FOR 1 (SWY.CVR1, SAFEWAY INC - CVR FOR CASA LEY, 786CVR209)",
# "SWY(US7865142084) SPINOFF SWY.CVR1 1 FOR 1, 1 FOR 1 (SWY.CVR2, SAFEWAY INC - CVR FOR PDC, 786CVR308)",
# "GYRO.NOTE(US403NOTE034) SPINOFF  1 FOR 40 (GYRO.NTS2, GYRODYNE CO OF AMERICA INC - GLOBAL DIVIDEND NOTE - PIK, 403PIK103)",
# "SWY(US7865142084) MERGED(Acquisition)  FOR USD 34.91200000 PER SHARE (SWY, SAFEWAY INC, 786514208)",
# "SGGHU(US82670K1280) TENDERED TO US8269922402 1 FOR 1 (SGGHU, SIGNATURE GROUP HOLDINGS INC, 82670K128)",
# "SGGHU(US82670K1280) TENDERED TO US8269922402 1 FOR 1 (SGGHU.EX, SIGNATURE GROUP HOLDINGS INC - BASIC SUBSCRIPTION, 826992240)",
# "SGGHU.EX(US8269922402) MERGED(Voluntary Offer Allocation)  WITH SGRH 1 FOR 1,US8269922576 562 FOR 10 (20150224001800SGGHU, SIGNATURE GROUP HOLDINGS COMMON STOCK, 826992257)",
# "SGGHU(US82670K1280) TENDERED TO US8269922402 1 FOR 1 (SGGHU, SIGNATURE GROUP HOLDINGS INC, 82670K128)",
# "SGGHU.EX(US8269922402) MERGED(Voluntary Offer Allocation)  WITH SGRH 1 FOR 1,US8269922576 562 FOR 10 (SGGHU.EX, SIGNATURE GROUP HOLDINGS INC - BASIC SUBSCRIPTION, 826992240)",
# "SGGHU.EX(US8269922402) MERGED(Voluntary Offer Allocation)  WITH SGRH 1 FOR 1,US8269922576 562 FOR 10 (SGRH, SIGNATURE GROUP HOLDINGS INC, 82670K201)",
# "SGGHU(US8269922576) MERGED(Voluntary Offer Allocation)  WITH US82670K2015 1 FOR 1 (20150224001800SGGHU, SIGNATURE GROUP HOLDINGS COMMON STOCK, 826992257)",
# "SGGHU(US8269922576) MERGED(Voluntary Offer Allocation)  WITH US82670K2015 1 FOR 1 (SGRH, SIGNATURE GROUP HOLDINGS INC, 82670K201)",
# "PRXI(US74051E1029) SPLIT 1 FOR 10 (PRXI, PREMIER EXHIBITIONS INC, 74051E201)",
# "PRXI(US74051E1029) SPLIT 1 FOR 10 (PRXI.OLD, PREMIER EXHIBITIONS INC, 74051E102)",
# "WMI SECON(US92936PAB67) STOCK DIVIDEND 325 FOR 10000 (WMI SECON, WMI HLDGS CORP 13% SECOND LIEN NOTE 03/16/2030, 92936PAB6)",
# "WMI FIRST(US92936PAA84) MERGED(Acquisition)  FOR USD 1.00000000 PER SHARE (WMI FIRST, WMI HLDGS CORP 13% FIRST LIEN NOTE 03/19/2030, 92936PAA8)",
# "AMP(ES0109260531) SUBSCRIBABLE RIGHTS ISSUE  1 FOR 1 (AMP.D, AMPER SA - BONUS RTS, ES0609260924)",
# "AMP(ES0109260531) SPINOFF  1 FOR 1 (AMP.D, AMPER SA - BONUS RTS, ES0609260924)",
# "AMP(ES0109260531) SPINOFF  1 FOR 1 (AMP.D, AMPER SA - BONUS RTS, ES0609260924)",
# "AMPDe (ES0609260924) SUBSCRIBES TO () (AMP.RTS2, AMPER SA - SUBRTS150605, SUBAMP150605)",
# "OVER SUBSCRIBE AMP.RTS3 (OVEAMP150605) AT 0.05 EUR (AMP.RTS3, AMPER SA - OVERTS150605, OVEAMP150605)",
# "AMPDe (ES0609260924) SUBSCRIBES TO () (AMPDe, AMPER SA-RTS, ES0609260924)",
# "GYRO(US4038201038) SUBSCRIBABLE RIGHTS ISSUE  3 FOR 2 (GYRO.RTS, GYRODYNE CO OF AMERICA INC - RIGHTS - EXPIRE 6/17/15, 403991094)",
# "GYRO(US4038201038) SUBSCRIBABLE RIGHTS ISSUE  3 FOR 2 (GYRO.RTS, GYRODYNE CO OF AMERICA INC - RIGHTS - EXPIRE 6/17/15, 403991094)",
# "NTP(G63907102) TENDERED TO G63990264 1 FOR 1 (NTP, NAM TAI PROPERTY INC, VGG639071023)",
# "NTP(G63907102) TENDERED TO G63990264 1 FOR 1 (NTP.TEN, NAM TAI PROPERTY INC - TENDER, VGG639902649)",
# "AMP.RTS2(SUBAMP150605) MERGED(Voluntary Offer Allocation)  WITH ES0109260531 1 FOR 1 (AMP, AMPER SA, ES0109260531)",
# "AMP.RTS3(OVEAMP150605) MERGED(Voluntary Offer Allocation)  WITH ES0109260531 1 FOR 1 (AMP, AMPER SA, ES0109260531)",
# "AMP.RTS2(SUBAMP150605) MERGED(Voluntary Offer Allocation)  WITH ES0109260531 1 FOR 1 (AMP.RTS2, AMPER SA - SUBRTS150605, SUBAMP150605)",
# "AMP.RTS3(OVEAMP150605) MERGED(Voluntary Offer Allocation)  WITH ES0109260531 1 FOR 1 (AMP.RTS3, AMPER SA - OVERTS150605, OVEAMP150605)",
# "(ES0609260924) DELISTED (AMPDe, AMPER SA-RTS, ES0609260924)",
# "RELY(US82670K2015) CUSIP/ISIN CHANGE TO (US75601W1045) (RELY, REAL INDUSTRY INC, 75601W104)",
# "RELY(US82670K2015) CUSIP/ISIN CHANGE TO (US75601W1045) (RELY.OLD, SIGNATURE GROUP HOLDINGS INC, 82670K201)",
# "NTP(G63907102) TENDERED TO G63990264 1 FOR 1 (NTP, NAM TAI PROPERTY INC, VGG639071023)",
# "NTP(G63907102) TENDERED TO G63990264 1 FOR 1 (NTP.TEN, NAM TAI PROPERTY INC - TENDER, VGG639902649)",
# "NTP.TEN(VGG639902649) MERGED(Voluntary Offer Allocation)  FOR USD 5.50000000 PER SHARE (NTP.TEN, NAM TAI PROPERTY INC - TENDER, VGG639902649)",
# "IFT(US4528341047) SUBSCRIBABLE RIGHTS ISSUE  1 FOR 4 (IFT.RTS, IMPERIAL HOLDINGS INC - RIGHTS, 452994999)",
# "IFT(US4528341047) SUBSCRIBABLE RIGHTS ISSUE  1 FOR 4 (IFT.RTS, IMPERIAL HOLDINGS INC - RIGHTS, 452994999)",
# "IFT.RTS (US4529949996) SUBSCRIBES TO () (IFT.EX, IMPERIAL HOLDINGS INC - BASIC RIGHTS SUBSCRIPTION, 45283410E)",
# "OVER SUBSCRIBE IFT.OS (US45283410OS) AT 5.75 USD (IFT.OS, IMPERIAL HOLDINGS INC - RIGHTS OVERSUBSCRIPTION, 45283410O)",
# "IFT.RTS (US4529949996) SUBSCRIBES TO () (IFT.RTS, IMPERIAL HOLDINGS INC - RIGHTS, 452994999)",
# "GYRO.RTS (US4039910942) SUBSCRIBES TO () (GYRO.EX, GYRODYNE CO OF AMERICA INC - BASIC RIGHTS SUBSCRIPTION, 40382010E)",
# "OVER SUBSCRIBE GYRO.OS (US40382010OS) AT 2.75 USD (GYRO.OS, GYRODYNE CO OF AMERICA INC - RIGHTS OVERSUBSCRIPTION, 40382010O)",
# "GYRO.RTS (US4039910942) SUBSCRIBES TO () (GYRO.RTS, GYRODYNE CO OF AMERICA INC - RIGHTS - EXPIRE 6/17/15, 403991094)",
# "GYRO.EX(US40382010EX) MERGED(Voluntary Offer Allocation)  WITH US4038201038 1 FOR 1 (GYRO, GYRODYNE CO OF AMERICA INC, 403820103)",
# "GYRO.OS(US40382010OS) MERGED(Voluntary Offer Allocation)  WITH US4038201038 1 FOR 1 (GYRO, GYRODYNE CO OF AMERICA INC, 403820103)",
# "GYRO.EX(US40382010EX) MERGED(Voluntary Offer Allocation)  WITH US4038201038 1 FOR 1 (GYRO.EX, GYRODYNE CO OF AMERICA INC - BASIC RIGHTS SUBSCRIPTION, 40382010E)",
# "OVER SUBSCRIBE GYRO.OS (US40382010OS) AT 2.75 USD (GYRO.OS, GYRODYNE CO OF AMERICA INC - RIGHTS OVERSUBSCRIPTION, 40382010O)",
# "GYRO.OS(US40382010OS) MERGED(Voluntary Offer Allocation)  WITH US4038201038 1 FOR 1 (GYRO.OS, GYRODYNE CO OF AMERICA INC - RIGHTS OVERSUBSCRIPTION, 40382010O)",
# "IFT.EX(US45283410EX) MERGED(Voluntary Offer Allocation)  WITH US4528341047 1 FOR 1 (IFT, IMPERIAL HOLDINGS INC, 452834104)",
# "IFT.OS(US45283410OS) MERGED(Voluntary Offer Allocation)  WITH US4528341047 1 FOR 1 (IFT, IMPERIAL HOLDINGS INC, 452834104)",
# "IFT.EX(US45283410EX) MERGED(Voluntary Offer Allocation)  WITH US4528341047 1 FOR 1 (IFT.EX, IMPERIAL HOLDINGS INC - BASIC RIGHTS SUBSCRIPTION, 45283410E)",
# "IFT.OS(US45283410OS) MERGED(Voluntary Offer Allocation)  WITH US4528341047 1 FOR 1 (IFT.OS, IMPERIAL HOLDINGS INC - RIGHTS OVERSUBSCRIPTION, 45283410O)",
# "GHC(US3846371041) SPINOFF  1 FOR 1 (CABO, CABLE ONE INC-W/I, 12685J105)",
# "GYRO(US4038201038) SPINOFF  46 FOR 100 (GYRO.NTS3, GYRODYNE CO OF AMERICA INC - 5% SUBORDINATED NOTE - 12/31/14, 40INT0103)",
# "GYRO(US4038201038) SPINOFF  46 FOR 100 (GYRO.NTS3, GYRODYNE CO OF AMERICA INC - 5% SUBORDINATED NOTE - 12/31/14, 40INT0103)",
# "VSW(US92534R1023) MERGED(Acquisition)  WITH US67021T2096 1 FOR 1 (NTENT, NTENT INC, 67021T209)",
# "VSW(US92534R1023) MERGED(Acquisition)  WITH US67021T2096 1 FOR 1 (VSW, VERTICAL SEARCH WORKS, INC. - PRIVATE COMPANY, 92534R102)",
# "GYRO.NOTE(US403NOTE034) SPINOFF  1 FOR 40 (GYRO.NTS2, GYRODYNE CO OF AMERICA INC - GLOBAL DIVIDEND NOTE - PIK, 403PIK103)",
# "IFT(US4528341047) CUSIP/ISIN CHANGE TO (US29102N1054) (EMG, EMERGENT CAPITAL INC, 29102N105)",
# "IFT(US4528341047) CUSIP/ISIN CHANGE TO (US29102N1054) (IFT.OLD, IMPERIAL HOLDINGS INC, 452834104)",
# "GYRO(US4038201038) SPINOFF  46 FOR 100 (GYRO.NTS3, GYRODYNE CO OF AMERICA INC - 5% SUBORDINATED NOTE - 12/31/14, 40INT0103)",
# "GYRO(US4038201038) SPINOFF  46 FOR 100 (GYRO.NTS3, GYRODYNE CO OF AMERICA INC - 5% SUBORDINATED NOTE - 12/31/14, 40INT0103)",
# "NTP(G63907102) TENDERED TO G63990272 1 FOR 1 (NTP, NAM TAI PROPERTY INC, VGG639071023)",
# "NTP(G63907102) TENDERED TO G63990272 1 FOR 1 (NTP.TEN, NAM TAI PROPERTY INC - TENDER, VGG639902722)",
# "NTP.TEN(G63990272) MERGED(Voluntary Offer Allocation)  FOR USD 5.50000000 PER SHARE (NTP.TEN, NAM TAI PROPERTY INC - TENDER, VGG639902722)",
# "GYRO.NOTE(US403NOTE034) MERGED(Acquisition)  WITH US4038291047 24798 FOR 1000000 (20140822144148GYRO.NOTE, GYRODYNE CO OF AMERICA INC - 10.89 NON-TRANSFERABLE NOTES, 403NOTE03)",
# "GYRO.NTS2(US403PIK1030) MERGED(Acquisition)  WITH US4038291047 24798 FOR 1000000 (GYRO, GYRODYNE LLC, 403829104)",
# "GYRO.NOTE(US403NOTE034) MERGED(Acquisition)  WITH US4038291047 24798 FOR 1000000 (GYRO, GYRODYNE LLC, 403829104)",
# "GYRO.NTS2(US403PIK1030) MERGED(Acquisition)  WITH US4038291047 24798 FOR 1000000 (GYRO.NTS2, GYRODYNE CO OF AMERICA INC - GLOBAL DIVIDEND NOTE - PIK, 403PIK103)",
# "GYRO.NTS(US4038NOTE30) MERGED(Acquisition)  WITH US4038291047 474 FOR 1000 (GYRO, GYRODYNE LLC, 403829104)",
# "GYRO.NTS(US4038NOTE30) MERGED(Acquisition)  WITH US4038291047 474 FOR 1000 (GYRO.NTS, GYRODYNE CO OF AMERICA INC - 20.70 INTERESTS, 4038NOTE3)",
# "GYRO.NTS3(US40INT01039) MERGED(Acquisition)  WITH US4038291047 24798 FOR 1000000 (GYRO, GYRODYNE LLC, 403829104)",
# "GYRO.NTS3(US40INT01039) MERGED(Acquisition)  WITH US4038291047 24798 FOR 1000000 (GYRO.NTS3, GYRODYNE CO OF AMERICA INC - 5% SUBORDINATED NOTE - 12/31/14, 40INT0103)",
# "GYRO(US4038201038) SPINOFF  46 FOR 100 (GYRO.NTS3, GYRODYNE CO OF AMERICA INC - 5% SUBORDINATED NOTE - 12/31/14, 40INT0103)",
# "GYRO(US4038201038) SPINOFF  46 FOR 100 (GYRO.NTS3, GYRODYNE CO OF AMERICA INC - 5% SUBORDINATED NOTE - 12/31/14, 40INT0103)",
# "GYRO.NTS3(US40INT01039) MERGED(Acquisition)  WITH US4038291047 24798 FOR 1000000 (GYRO, GYRODYNE LLC, 403829104)",
# "GYRO.NTS3(US40INT01039) MERGED(Acquisition)  WITH US4038291047 24798 FOR 1000000 (GYRO.NTS3, GYRODYNE CO OF AMERICA INC - 5% SUBORDINATED NOTE - 12/31/14, 40INT0103)",
# "WMI SECON(DUMMYBONDPAB) MERGED(Acquisition)  WITH US92936PAB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92CALLAB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "NWLI(US6385221022) CUSIP/ISIN CHANGE TO (US6385171029) (NWLI, NATL WESTERN LIFE INS-CL A, 638517102)",
# "NWLI(US6385221022) CUSIP/ISIN CHANGE TO (US6385171029) (NWLI.OLD, NATL WESTERN LIFE INS-CL A, 638522102)",
# "WMI SECON(DUMMYBONDPAB) MERGED(Acquisition)  WITH US92936PAB67 1 FOR 1 (WMI SECON, WMI HLDGS CORP 13% SECOND LIEN NOTE 03/16/2030, DUMMYBONDPAB)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92CALLAB67 1 FOR 1 (WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, 92CALLAB6)",
# "TPHS(US89656D1019) SUBSCRIBABLE RIGHTS ISSUE  248362 FOR 1000000 (TPHS.RTS, TRINITY PLACE HOLDINGS INC - RIGHTS, 896994027)",
# "TPHS.RTS (US8969940274) SUBSCRIBES TO () (TPHS.EX, TRINITY PLACE HOLDINGS INC - RIGHTS SUBSCRIPTION, 89656D10E)",
# "OVER SUBSCRIBE TPHS.OS (US89656D10OS) AT 6.00 USD (TPHS.OS, TRINITY PLACE HOLDINGS INC - RIGHTS OVERSUBSCRIPTION, 89656D10O)",
# "TPHS.RTS (US8969940274) SUBSCRIBES TO () (TPHS.RTS, TRINITY PLACE HOLDINGS INC - RIGHTS, 896994027)",
# "92CALLAB6(US92CALLAB67) MERGED(Voluntary Offer Allocation)  FOR USD 1.00000000 PER SHARE (WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, 92CALLAB6)",
# "OVSPA(US69036R2022) STOCK DIVIDEND 1 FOR 10 (OVSPA, OVERSEAS SHIPHOL-ACCD INV A, 69036R202)",
# "TPHS.OS(US89656D10OS) MERGED(Voluntary Offer Allocation)  WITH US89656D1019 1 FOR 1 (TPHS, TRINITY PLACE HOLDINGS INC, 89656D101)",
# "TPHS.EX(US89656D10EX) MERGED(Voluntary Offer Allocation)  WITH US89656D1019 1 FOR 1 (TPHS, TRINITY PLACE HOLDINGS INC, 89656D101)",
# "TPHS.EX(US89656D10EX) MERGED(Voluntary Offer Allocation)  WITH US89656D1019 1 FOR 1 (TPHS.EX, TRINITY PLACE HOLDINGS INC - RIGHTS SUBSCRIPTION, 89656D10E)",
# "TPHS.OS(US89656D10OS) MERGED(Voluntary Offer Allocation)  WITH US89656D1019 1 FOR 1 (TPHS.OS, TRINITY PLACE HOLDINGS INC - RIGHTS OVERSUBSCRIPTION, 89656D10O)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92CALLAB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92CALLAB67 1 FOR 1 (WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, 92CALLAB6)",
# "92CALLAB6(US92CALLAB67) MERGED(Full Call)  FOR USD 1.00000000 PER SHARE (WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, 92CALLAB6)",
# "OVSPA(US69036R2022) MERGED(Acquisition)  WITH US69036R3012 1 FOR 1 (OSG, OVERSEAS SHIPHOLDING GROUP-A, 69036R301)",
# "OVSPA(US69036R2022) MERGED(Acquisition)  WITH US69036R3012 1 FOR 1 (OVSPA, OVERSEAS SHIPHOL-ACCD INV A, 69036R202)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30 LLB6, WMIH 13 03/19/30 - PARTIAL CALL RED DATE 7/1, 929CALLB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30 LLB6, WMIH 13 03/19/30 - PARTIAL CALL RED DATE 7/1, 929CALLB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30 LLB6, WMIH 13 03/19/30 - PARTIAL CALL RED DATE 7/1, 929CALLB6)",
# "OSG(US69036R3012) SPLIT 1 FOR 6 (OSG, OVERSEAS SHIPHOLDING GROUP-A, 69036R863)",
# "OSG(US69036R3012) SPLIT 1 FOR 6 (OSG.OLD, OVERSEAS SHIPHOLDING GROUP-A, 69036R301)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30 LLB6, WMIH 13 03/19/30 - PARTIAL CALL RED DATE 7/1, 929CALLB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30 LLB6, WMIH 13 03/19/30 - PARTIAL CALL RED DATE 7/1, 929CALLB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US929CALLB67 1 FOR 1 (WMIH 13 03/19/30 LLB6, WMIH 13 03/19/30 - PARTIAL CALL RED DATE 7/1, 929CALLB6)",
# "OSG(US69036R3012) SPLIT 1 FOR 6 (OSG, OVERSEAS SHIPHOLDING GROUP-A, 69036R863)",
# "OSG(US69036R3012) SPLIT 1 FOR 6 (OSG.OLD, OVERSEAS SHIPHOLDING GROUP-A, 69036R301)",
# "(US929CALLB67) BOND MATURITY FOR USD 1.00000000 PER BOND (WMIH 13 03/19/30 LLB6, WMIH 13 03/19/30 - PARTIAL CALL RED DATE 7/1, 929CALLB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92936CALL7 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92936CALL7 1 FOR 1 (WMIH 13 03/19/30 CALL, WMIH 13 03/19/30 - PARTIAL CALL RED DATE 10/1, 92936CALL)",
# "VXX(US06742E7114) SPLIT 1 FOR 4 (VXX, IPATH S&amp;P 500 VIX S/T FU ETN, 06740Q252)",
# "VXX(US06742E7114) SPLIT 1 FOR 4 (VXX.OLD, IPATH S&amp;P 500 VIX S/T FU ETN, 06742E711)",
# "(US92936CALL7) BOND MATURITY FOR USD 1.00000000 PER BOND (WMIH 13 03/19/30 CALL, WMIH 13 03/19/30 - PARTIAL CALL RED DATE 10/1, 92936CALL)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92CALLAB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92CALLAB67 1 FOR 1 (WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, 92CALLAB6)",
# "92CALLAB6(US92CALLAB67) MERGED(Partial Call)  FOR USD 1.00000000 PER SHARE (WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, 92CALLAB6)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92CALLAB67 1 FOR 1 (WMIH 13 03/19/30, WMIH 13 03/19/30, 92936PAB6)",
# "TPHS(US89656D1019) SUBSCRIBABLE RIGHTS ISSUE  126093 FOR 1000000 (TPHSR, TRINITY PLACE HOLDINGS INC - RIGHTS, 896994175)",
# "WMIH 13 03/19/30(US92936PAB67) TENDERED TO US92CALLAB67 1 FOR 1 (WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, 92CALLAB6)",
# "TPHSR (US8969941751) SUBSCRIBES TO () (TPHS.EX, TRINITY PLACE HOLDINGS INC - RIGHTS SUBSCRIPTION, 89656R10E)",
# "TPHSR (US8969941751) SUBSCRIBES TO () (TPHSR, TRINITY PLACE HOLDINGS INC - RIGHTS, 896994175)",
# "92CALLAB6(US92CALLAB67) MERGED(Partial Call)  FOR USD 1.00000000 PER SHARE (WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, WMI HLDGS CORP 13% SEC LIEN NT 03/16/2030 - PARTIAL CALL, 92CALLAB6)",
# "TPHS.EX(US89656R10EX) MERGED(Voluntary Offer Allocation)  WITH US89656D1019 1 FOR 1 (TPHS, TRINITY PLACE HOLDINGS INC, 89656D101)",
# "TPHS.EX(US89656R10EX) MERGED(Voluntary Offer Allocation)  WITH US89656D1019 1 FOR 1 (TPHS.EX, TRINITY PLACE HOLDINGS INC - RIGHTS SUBSCRIPTION, 89656R10E)", ]
