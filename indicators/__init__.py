"""指标类库
含各类指标及计算方法
- Ta-Lib  可以用下载 https://www.lfd.uci.edu/~gohlke/pythonlibs/
    若本机安装是32位的python3.6，则选TA_Lib‑0.4.17‑cp36‑cp36m‑win32.whl下载
    pip install TA_Lib-0.4.17-cp37-cp37m-win_amd64.whl
- akshare 安装
    https://github.com/akfamily/akshare/releases/tag/release-v1.8.26
    python setup.py build
    python setup.py install
"""
import talib

"""
指标群组：
    - Overlap Studies 重叠研究
        BBANDS               Bollinger Bands #布林带
        DEMA                 Double Exponential Moving Average #双指数移动平均线
        EMA                  Exponential Moving Average #指数滑动平均
        HT_TRENDLINE         Hilbert Transform - Instantaneous Trendline #希尔伯特变换瞬时趋势
        KAMA                 Kaufman Adaptive Moving Average #卡玛考夫曼自适应移动平均
        MA                   Moving average #均线
        MAMA                 MESA Adaptive Moving Average #自适应移动平均 
        MAVP                 Moving average with variable period #变周期移动平均
        MIDPOINT             MidPoint over period #在周期的中点
        MIDPRICE             Midpoint Price over period #中间时段价格
        SAR                  Parabolic SAR #抛物线转向指标
        SAREXT               Parabolic SAR - Extended #抛物线转向指标 - 扩展
        SMA                  Simple Moving Average# 简单移动平均线
        T3                   Triple Exponential Moving Average (T3)
        TEMA                 Triple Exponential Moving Average
        TRIMA                Triangular Moving Average
        WMA                  Weighted Moving Average#加权移动平均线
    - Momentum Indicators 动量指标
        ADX                  Average Directional Movement Index
        ADXR                 Average Directional Movement Index Rating
        APO                  Absolute Price Oscillator
        AROON                Aroon
        AROONOSC             Aroon Oscillator
        BOP                  Balance Of Power
        CCI                  Commodity Channel Index
        CMO                  Chande Momentum Oscillator
        DX                   Directional Movement Index
        MACD                 Moving Average Convergence/Divergence
        MACDEXT              MACD with controllable MA type
        MACDFIX              Moving Average Convergence/Divergence Fix 12/26
        MFI                  Money Flow Index
        MINUS_DI             Minus Directional Indicator
        MINUS_DM             Minus Directional Movement
        MOM                  Momentum
        PLUS_DI              Plus Directional Indicator
        PLUS_DM              Plus Directional Movement
        PPO                  Percentage Price Oscillator
        ROC                  Rate of change : ((price/prevPrice)-1)*100
        ROCP                 Rate of change Percentage: (price-prevPrice)/prevPrice
        ROCR                 Rate of change ratio: (price/prevPrice)
        ROCR100              Rate of change ratio 100 scale: (price/prevPrice)*100
        RSI                  Relative Strength Index
        STOCH                Stochastic
        STOCHF               Stochastic Fast
        STOCHRSI             Stochastic Relative Strength Index
        TRIX                 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
        ULTOSC               Ultimate Oscillator
        WILLR                Williams' %R
    - Volume Indicators 成交量指标
        AD                   Chaikin A/D Line
        ADOSC                Chaikin A/D Oscillator
        OBV                  On Balance Volume
    - Volatility Indicators 波动性指标
        ATR                  Average True Range
        NATR                 Normalized Average True Range
        TRANGE               True Range
    - Price Transform 价格指标
        AVGPRICE             Average Price
        MEDPRICE             Median Price
        TYPPRICE             Typical Price
        WCLPRICE             Weighted Close Price
    - Cycle Indicators 周期指标
        HT_DCPERIOD          Hilbert Transform - Dominant Cycle Period
        HT_DCPHASE           Hilbert Transform - Dominant Cycle Phase
        HT_PHASOR            Hilbert Transform - Phasor Components
        HT_SINE              Hilbert Transform - SineWave
        HT_TRENDMODE         Hilbert Transform - Trend vs Cycle Mode
    - Pattern Recognition 形态识别
        CDL2CROWS            Two Crows
        CDL3BLACKCROWS       Three Black Crows
        CDL3INSIDE           Three Inside Up/Down
        CDL3LINESTRIKE       Three-Line Strike
        CDL3OUTSIDE          Three Outside Up/Down
        CDL3STARSINSOUTH     Three Stars In The South
        CDL3WHITESOLDIERS    Three Advancing White Soldiers
        CDLABANDONEDBABY     Abandoned Baby
        CDLADVANCEBLOCK      Advance Block
        CDLBELTHOLD          Belt-hold
        CDLBREAKAWAY         Breakaway
        CDLCLOSINGMARUBOZU   Closing Marubozu
        CDLCONCEALBABYSWALL  Concealing Baby Swallow
        CDLCOUNTERATTACK     Counterattack
        CDLDARKCLOUDCOVER    Dark Cloud Cover
        CDLDOJI              Doji
        CDLDOJISTAR          Doji Star
        CDLDRAGONFLYDOJI     Dragonfly Doji
        CDLENGULFING         Engulfing Pattern
        CDLEVENINGDOJISTAR   Evening Doji Star
        CDLEVENINGSTAR       Evening Star
        CDLGAPSIDESIDEWHITE  Up/Down-gap side-by-side white lines
        CDLGRAVESTONEDOJI    Gravestone Doji
        CDLHAMMER            Hammer
        CDLHANGINGMAN        Hanging Man
        CDLHARAMI            Harami Pattern
        CDLHARAMICROSS       Harami Cross Pattern
        CDLHIGHWAVE          High-Wave Candle
        CDLHIKKAKE           Hikkake Pattern
        CDLHIKKAKEMOD        Modified Hikkake Pattern
        CDLHOMINGPIGEON      Homing Pigeon
        CDLIDENTICAL3CROWS   Identical Three Crows
        CDLINNECK            In-Neck Pattern
        CDLINVERTEDHAMMER    Inverted Hammer
        CDLKICKING           Kicking
        CDLKICKINGBYLENGTH   Kicking - bull/bear determined by the longer marubozu
        CDLLADDERBOTTOM      Ladder Bottom
        CDLLONGLEGGEDDOJI    Long Legged Doji
        CDLLONGLINE          Long Line Candle
        CDLMARUBOZU          Marubozu
        CDLMATCHINGLOW       Matching Low
        CDLMATHOLD           Mat Hold
        CDLMORNINGDOJISTAR   Morning Doji Star
        CDLMORNINGSTAR       Morning Star
        CDLONNECK            On-Neck Pattern
        CDLPIERCING          Piercing Pattern
        CDLRICKSHAWMAN       Rickshaw Man
        CDLRISEFALL3METHODS  Rising/Falling Three Methods
        CDLSEPARATINGLINES   Separating Lines
        CDLSHOOTINGSTAR      Shooting Star
        CDLSHORTLINE         Short Line Candle
        CDLSPINNINGTOP       Spinning Top
        CDLSTALLEDPATTERN    Stalled Pattern
        CDLSTICKSANDWICH     Stick Sandwich
        CDLTAKURI            Takuri (Dragonfly Doji with very long lower shadow)
        CDLTASUKIGAP         Tasuki Gap
        CDLTHRUSTING         Thrusting Pattern
        CDLTRISTAR           Tristar Pattern
        CDLUNIQUE3RIVER      Unique 3 River
        CDLUPSIDEGAP2CROWS   Upside Gap Two Crows
        CDLXSIDEGAP3METHODS  Upside/Downside Gap Three Methods
    - Statistic Functions 统计函数
        BETA                 Beta
        CORREL               Pearson's Correlation Coefficient (r)
        LINEARREG            Linear Regression
        LINEARREG_ANGLE      Linear Regression Angle
        LINEARREG_INTERCEPT  Linear Regression Intercept
        LINEARREG_SLOPE      Linear Regression Slope
        STDDEV               Standard Deviation
        TSF                  Time Series Forecast
        VAR                  Variance
    - Math Transform 数学变换
        
    - Math Operators 数学运算符
"""

print('所有可用指标：')
print('所有指标列表：', talib.get_functions())
print('指标群组：', talib.get_function_groups())
