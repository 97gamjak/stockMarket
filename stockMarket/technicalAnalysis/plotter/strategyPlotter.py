import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from stockMarket.technicalAnalysis.strategy import Strategy
from stockMarket.technicalAnalysis._common import finalize
from stockMarket.technicalAnalysis.trade import TradeOutcome, TradeStatus


class StrategyPlotter:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        self.finalize_commands = strategy.finalize_commands

        self.trades = np.concatenate(list(strategy.trades.values()))

    def plot_all(self):
        self.plot_PL_histogram()
        self.plot_trades_vs_time()

    @finalize
    def plot_PL_histogram(self,
                          bin_size: float = 0.25,
                          min_bin: float = 0.0,
                          max_bin: float = 6.0,
                          ) -> None:

        bins = np.arange(min_bin, max_bin, bin_size)
        bins = np.append(bins, np.inf)

        win_mask = self.trades['outcome_status'] == TradeOutcome.WIN
        win_PL = self.trades[win_mask]['PL']

        loss_mask = self.trades['outcome_status'] == TradeOutcome.LOSS
        loss_PL = self.trades[loss_mask]['PL']

        # Calculate the counts of win and loss PL values in each bin
        win_PL_per_bin, _ = np.histogram(win_PL)
        loss_PL_per_bin, _ = np.histogram(loss_PL)

        # Calculate the total number of trades in each bin
        total_trades_per_bin = win_PL_per_bin + loss_PL_per_bin

        # Calculate the effective and theoretical PL ratio for each bin
        PL_ratio_effective = np.zeros_like(win_PL_per_bin)
        np.divide(
            win_PL_per_bin,
            total_trades_per_bin,
            out=PL_ratio_effective,
            where=total_trades_per_bin != 0
        )
        PL_ratio_theoretical = np.mean(
            np.concatenate((win_PL_per_bin, loss_PL_per_bin)),
            axis=0
        )

        # Create a figure and a subplot
        _, ax1 = plt.subplots()

        # Plot the histogram on ax1
        ax1.hist([win_PL, loss_PL], bins=bins, alpha=0.5,
                 label=['win', 'loss'], stacked=True, color=["g", "r"])
        ax1.set_ylabel('Count win/loss trades')
        ax1.set_xlabel('theoretical PL ratio')
        ax1.legend(loc='upper left')

        # Create a second y-axis
        ax2 = ax1.twinx()

        PL_ratio_normed = PL_ratio_effective - 1/(PL_ratio_theoretical + 1)

        # Plot the PL ratio on ax2
        ax2.plot(
            PL_ratio_theoretical,
            PL_ratio_normed,
            color='k',
            label='excess win percentage'
        )
        # make this axis in percent
        ax2.set_yticklabels(['{:,.0%}'.format(x) for x in ax2.get_yticks()])
        ax2.hlines(0, 0, 6, color='k', linestyle='--')
        ax2.set_ylabel('excess win percentage')
        ax2.legend(loc='upper right')

        plt.tight_layout()
        plt.savefig(str(self.strategy.dir_path / "PL_histogram.png"))

    @finalize
    def plot_trades_vs_time(self, max_loss: float = 1.0):

        # Create a DataFrame from the trades
        trades_df = pd.DataFrame(self.trades)
        trades_df['INVESTMENT'] = trades_df['INVESTMENT'] * max_loss
        trades_df['OUTCOME'] = trades_df['OUTCOME'] * max_loss

        # Set the date range
        date_range = pd.date_range(
            start=self.strategy.start_date,
            end=pd.Timestamp.now().date(),
            freq='D'
        )

        # Initialize the result DataFrame
        result_df = pd.DataFrame(index=date_range)
        result_df['amount_trades'] = 0
        result_df['total_invested'] = 0.0
        result_df['total_outcome'] = 0.0

        # Calculate the total outcome for closed trades
        closed_trades = trades_df[trades_df.trade_status == TradeStatus.CLOSED]
        result_df.loc[closed_trades.EXIT_date,
                      'total_outcome'] += (closed_trades.OUTCOME).values

        # Calculate the amount of trades and total invested for open trades and trades that have not exited yet
        open_trades = trades_df[
            (trades_df.trade_status == TradeStatus.OPEN) |
            (trades_df.EXIT_date >= result_df.index)
        ]
        result_df.loc[open_trades.ENTRY_date, 'amount_trades'] += 1
        result_df.loc[open_trades.ENTRY_date,
                      'total_invested'] += (open_trades.INVESTMENT).values

        # Forward fill the result DataFrame to propagate the last valid observation forward to the next valid
        result_df.ffill()

        max_edit_date = result_df[result_df['amount_trades'] != 0].index.max()
        result_df = result_df[:max_edit_date]

        _, ax = plt.subplots(1, 3, figsize=(30, 10))

        ax[0].plot(result_df.index, result_df['amount_trades'])
        ax[0].set_xlabel("Date", fontsize=18)
        ax[0].set_ylabel("Amount of trades", fontsize=18)

        ax[1].plot(result_df.index,
                   np.cumsum(result_df['total_invested']),
                   color="r"
                   )
        ax[1].set_ylabel("Total Invested in $", fontsize=18)
        ax[1].set_xlabel("Date", fontsize=18)

        ax[2].plot(
            result_df.index,
            np.cumsum(result_df['total_outcome']),
            color="g",
            label="Forward Total Outcome"
        )
        ax[2].plot(
            result_df.index,
            np.cumsum(result_df['total_outcome'][::-1]),
            color="b",
            label="Backward Total Outcome"
        )
        ax[2].set_ylabel("Total Outcome in $", fontsize=18)
        ax[2].set_xlabel("Date", fontsize=18)
        ax[2].legend(loc="upper left", fontsize=18)

        # make figure more compact
        plt.tight_layout()
        plt.savefig(str(self.strategy.dir_path / "trades_vs_time.png"))
