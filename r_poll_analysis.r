library(ggplot2)

polls_df <- read.csv("polls.csv")

labour <- polls_df$lab
tory <- polls_df$con

linear_model <- lm(labour ~ tory)
print(linear_model)

pollster_factors = factor(polls_df$pollster)
print(pollster_factors)

#plot(tory, labour)
#abline(linear_model)

#cor.test(tory, labour)

# In ggplot2
plot_linear_model <- geom_abline(intercept = 50, slope=-0.5)
plot_linear_model <- geom_smooth(method = "lm")

plot_xlims <- xlim(32, 44)
plot_ylims <- ylim(26, 36)

plot_points <- ggplot(polls_df, aes(con, lab)) + geom_point()
p <- plot_points + plot_linear_model + plot_ylims + plot_xlims
