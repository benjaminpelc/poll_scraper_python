# Analysis of General Election poll data
library(ggplot2)

# Prepare the environment
rm(list = ls())
setwd('~/Dropbox/Development/Python/pollwatch_2015-2020')

# Import the poll data
polls_file <- './polls.csv'
#polls_df = read.table(polls_file, header=TRUE, fill=TRUE, sep=',')
polls_df = read.csv(polls_file)

# Display some data
head(polls_df)
summary(polls_df)

# Extract the raw poll data
date <- as.Date(polls_df$endDate)
con <- polls_df$con
lab <- polls_df$lab
ukip <- polls_df$ukip
ldem <- polls_df$ldem

plot_raw_party_polls <- function(date_vector, scores_vector, party_colour, y_max) {
  plot(date_vector, scores_vector, ylim=c(0, y_max),
       col=party_colour,
       ylab="Score",
       xlab="Date",
       # filled dots
       pch=16)
}

moving_average <- function(xs, n=5) {
  filter(xs, rep(1/n, n), sides=2)
}

plot_raw_party_polls(date, con, "blue", 45)
# Do not overwrite plot
par(new=T)
plot_raw_party_polls(date, lab, "red", 45)
par(new=T)
plot_raw_party_polls(date, ukip, "purple", 45)
par(new=T)
plot_raw_party_polls(date, ldem, "yellow", 45)
grid()

par(new=T)
#plot(date, moving_average(con), ylim=c(0, 45),
#     col="blue",
#     ylab="Score",
#     xlab="Date",
#     type="l")

# make a scores matrix
scores_matrix = data.matrix(polls_df[6:10])
colnames(scores_matrix, c("con", "lab", "ukip", "ldem", "green"))

head(scores_matrix)
colMeans(scores_matrix)
