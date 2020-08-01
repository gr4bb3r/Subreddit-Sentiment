
def weighted_sentiments(scores,tickers):
    results = {}

    for b in range(len(tickers)):
        sum_scores = []
        scores_w8 =[]
        w8ted_scores = []
        for c in range(len(scores)):
            sum_scores.append(scores[c][tickers[b][0]][1])
            scores_w8.append([scores[c][tickers[b][0]][1],scores[c][tickers[b][0]][0]])
        temp_sumscr = sum(sum_scores)
        for d in scores_w8:
            if temp_sumscr == 0:
                continue
            else:
                w8ted_scores.append((d[0]/temp_sumscr) * d[1])
        results[[tickers[b][0]][0]] = [sum(sum_scores),sum(w8ted_scores)]
        
    return results