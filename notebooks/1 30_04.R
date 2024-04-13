setwd("D:/paklina/banks sentiment for index")

library(dplyr)
library(rvest)
library(RSelenium)
library(XML)
library(tidyr)
library(writexl)
library(readxl)

###### for one bank

get_bank_feeds = function(url_bank){

  da_bank = data.frame()
  i = 1

  repeat {

    print(i)

    url = paste0(url_bank, "?page=",i,"&isMobile=0")

    html = try(read_html(url))
    if (class(html) == "try-error") {break}

    feeds = html %>%
      html_nodes(".markup-inside-small") %>%
      html_text()

    if (length(feeds) == 0) {break}

    grades = html %>%
      html_nodes(".flexbox--align-items_baseline") %>%
      html_text()

    grades = extract_numeric(grades)

    frauds = html %>%
      html_nodes(".flexbox--align-items_baseline") %>%
      html_text()

    fraud = grepl("Не засчитана",frauds)

    date = html %>%
      html_nodes(".display-inline-block") %>%
      html_text()

    tmp = data.frame(url_bank, feeds, grades, fraud, date)

    da_bank = rbind(da_bank, tmp)

    i = i + 1

    Sys.sleep(runif(1,0,0.5))
  }

  return(da_bank)
}

##### list of banks

all_links = c()

for (i in 1:7){
  print(i)

  url = paste0("https://www.banki.ru/banks/?PAGEN_1=",i,"#results")

  html = read_html(url)

  links = html %>%
    html_nodes(".widget__link") %>%
    html_attr("href")

  links = gsub("/banks/bank", "https://www.banki.ru/services/responses/bank", links)

  all_links = c(all_links, links)
}

######

#all_links = read_xlsx("list.xlsx")
#all_links = all_links$list

all_banks_feeds = data.frame()

for (j in c(1:length(all_links))){

  print(j/length(all_links)*100)
  url_bank = all_links[j]

  d = get_bank_feeds(url_bank)

  all_banks_feeds = rbind(all_banks_feeds, d)

}


library(stringr)

all_banks_feeds2 = separate(all_banks_feeds, date, into = c("date", "time"), sep = " ")

all_banks_feeds2$date2 = dmy(all_banks_feeds2$date)
all_banks_feeds2$date = all_banks_feeds2$date2
all_banks_feeds2$date2 = NULL

writexl::write_xlsx(all_banks_feeds2, "all_banks_feeds_30_04.xlsx")
saveRDS(all_banks_feeds2, "all_banks_feeds_30_04.rds")

unique(all_banks_feeds$url_bank) %>% View()

###

d = readRDS("all_banks_feeds.rds")

all_banks_feeds$date2 = NULL

tmp = rbind(all_banks_feeds, d)

tmp = unique(tmp)

tmp2 = separate(tmp, date, into = c("date", "time"), sep = " ")

tmp2$date = dmy(tmp2$date)

saveRDS(tmp2, "all_banks_feeds_01_05.rds", compress = T)
