import logging


def compound_interest(rate, years):
    return (1 + rate) ** years


def total_dividend_disc(expected_rate, dividend, years):
    yearly_interest = [ compound_interest(rate=expected_rate, years=i) for i in range(1, years+1)]
    dividends_disc_yearly = map(lambda x: dividend / x, yearly_interest)
    return sum(dividends_disc_yearly)


class DCF:
    def __init__(self, cheap=None, normal=None, expensive=None):
        ''' Discounted Cash Flow (DCF)
            https://www.storm.mg/article/1546600
            payout ratio = dividends / EPS
        '''
        self.disc_rate_cheap = cheap or 0.13
        self.disc_rate_normal = normal or 0.09
        self.disc_rate_expensive = expensive or 0.03
        self.logger = logging.getLogger(__name__)

    def price(self, strike, PE, dividend, years):
        def _price(expected_rate):
            # Calc dividend discount rate
            dividends_disc = total_dividend_disc(expected_rate=expected_rate, dividend=dividend, years=years)
            return ((strike * PE) / compound_interest(rate=expected_rate, years=years)) + dividends_disc

        # Calc PE price
        return [ _price(expected_rate=self.disc_rate_cheap), 
                 _price(expected_rate=self.disc_rate_normal), 
                 _price(expected_rate=self.disc_rate_expensive)]



if __name__ == '__main__':
    dcf = DCF()
    # prices_table = dcf.price(strike=1, PE=12, dividend=0.6, years=10)
    # print(prices_table)

    # prices_table = dcf.price(strike=1, PE=15, dividend=0.6, years=10)
    # print(prices_table)
    
    # prices_table = dcf.price(strike=1, PE=20, dividend=0.6, years=10)
    # print(prices_table)

    # A17U
    prices_table = dcf.price(strike=3.21, PE=1, dividend=0.5252, years=1)
    print(3.21, prices_table)

    # APPL
    prices_table = dcf.price(strike=320, PE=1, dividend=0.2394, years=1)
    print(320, prices_table)

    # A7RU
    prices_table = dcf.price(strike=0.525, PE=1, dividend=3.48, years=1)
    print(0.525, prices_table)

    # SK6U.SI
    prices_table = dcf.price(strike=1.06, PE=1, dividend=0.95, years=1)
    print(1.06, prices_table)


