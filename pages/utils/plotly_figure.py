from datetime import datetime
import plotly.graph_objects as go
import dateutil
import pandas_ta as ta

def plotly_table(dataframe):
    header_color = 'grey'
    rowEvenColor = '#f8fafd'
    rowOddColor = '#e1efff'
    fill_colors = [rowOddColor if i % 2 == 0 else rowEvenColor for i in range(len(dataframe.columns) + 1)]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b><b>"] + ["<b>" + str(i)[:10] + "<b>" for i in dataframe.columns],
            line_color='#0078ff', fill_color='#0078ff',
            align='center', font=dict(color='white', size=15), height=35,
        ),
        cells=dict(
            values=[["<b>" + str(i) + "<b>" for i in dataframe.index]] + [dataframe[i] for i in dataframe.columns],
            fill_color=fill_colors,
            align='left', line_color=['white'], font=dict(color=['black'], size=15)
        )
    )])

    fig.update_layout(height=400, margin=dict(l=0, r=0, b=0, t=0))
    return fig 

def filter_date(dataframe, num_period):
    if num_period == '1mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-1)
    elif num_period == '5d':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(days=-5)
    elif num_period == '3mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-3)
    elif num_period == '6mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-6)
    elif num_period == '1y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-1)
    elif num_period == '5y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-5)
    elif num_period == 'ytd':
        date = datetime(dataframe.index[-1].year, 1, 1).strftime('%Y-%m-%d')
    else:
        date = dataframe.index[0]
    
    return dataframe.reset_index()[dataframe.reset_index()['Date']>date]


def close_chart(dataframe, num_period = False):
    if num_period:
        dataframe = filter_date(dataframe, num_period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Open'], mode='lines', name='Open', line=dict(color='#5ab7ff', width=2)))

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Close'], mode='lines', name='Close', line=dict(color='#ff7f0e', width=2)))

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['High'], mode='lines', name='High', line=dict(color='#2ca02c', width=2)))

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Low'], mode='lines', name='Low', line=dict(color='#d62728', width=2)))

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height = 500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor = 'white', paper_bgcolor = '#e1efff', legend=dict(
        yanchor="top",

        xanchor="right"
    ))
    return fig

def candlestick(dataframe, num_period):
    dataframe = filter_date(dataframe, num_period)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=dataframe['Date'], open=dataframe['Open'], high=dataframe['High'], low=dataframe['Low'], close=dataframe['Close']))

    fig.update_layout(showlegend=False, height = 500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor = 'white', paper_bgcolor = '#e1efff')
    return fig

def RSI(dataframe, num_period):
    dataframe['RSI'] = ta.rsi(dataframe['Close'])
    dataframe = filter_date(dataframe, num_period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe.RSI, name = 'RSI', marker_color='orange', line=dict(color='orange', width=2)))

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=[70] * len(dataframe), name = 'Overbought', marker_color='red', line=dict(color='red', width=1, dash='dash')))

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=[30] * len(dataframe), fill='tonexty', name = 'Oversold', marker_color='green', line=dict(color='green', width=1, dash='dash')))

    fig.update_layout(yaxis_range=[0, 100], height = 200, plot_bgcolor = 'white', paper_bgcolor = '#e1efff', margin=dict(l=0, r=0, t=0, b=0), legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="right", x=1))
    
    return fig

def Moving_Average(dataframe, num_period):
    dataframe['SMA_50'] = ta.sma(dataframe['Close'],50)
    dataframe = filter_date(dataframe, num_period)
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Open'], mode='lines', name='Open', line=dict(color='#5ab7ff', width=2)))

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Close'], mode='lines', name='Close', line=dict(color='#ff7f0e', width=2)))

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['High'], mode='lines', name='High', line=dict(color='#2ca02c', width=2)))

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Low'], mode='lines', name='Low', line=dict(color='#d62728', width=2)))

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['SMA_50'], mode='lines', name='SMA 50', line=dict(color='purple', width=2, dash='dash')))

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height = 500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor = 'white', paper_bgcolor = '#e1efff', legend=dict(
        yanchor="top",

        xanchor="right"
    ))
    return fig


def MACD(dataframe, num_period):
    macd = ta.macd(dataframe['Close']).iloc[:,0]
    macd_signal = ta.macd(dataframe['Close']).iloc[:,1]
    macd_histogram = ta.macd(dataframe['Close']).iloc[:,2]
    dataframe['MACD'] = macd
    dataframe['MACD_Signal'] = macd_signal
    dataframe['MACD_Histogram'] = macd_histogram
    dataframe = filter_date(dataframe, num_period)
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['MACD'], name = 'RSI', marker_color='orange', line=dict(color='orange', width=2)))
    
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['MACD_Signal'], name = 'Overbought', marker_color='red', line=dict(color='red', width=1, dash='dash')))
    c = ['red' if cl < 0 else 'green' for cl in macd_histogram]

    fig.update_layout(
        height = 200, plot_bgcolor = 'white', paper_bgcolor = '#e1efff', margin=dict(l=0, r=0, t=0, b=0), legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="right", x=1)
    )
    return fig


# Compatibility helpers (keeps the API used by pages/Stock_Analysis.py)
def line_chart(dataframe, num_period=False):
    return close_chart(dataframe, num_period=num_period)


def moving_average(dataframe, num_period):
    return Moving_Average(dataframe, num_period)

def moving_average_forecast(forecast):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=forecast.index[:-30], y=forecast['Close'][:-30], mode='lines', name='Close Price', line=dict(color='#ff7f0e', width=2)))

    fig.add_trace(go.Scatter(x=forecast.index[-31:], y=forecast['Close'].iloc[-31:], mode='lines', name='Forecasted Close Price', line=dict(color='purple', width=2)))

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height = 500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor = 'white', paper_bgcolor = '#e1efff', legend=dict(
        yanchor="top",

        xanchor="right"
    ))

    return fig