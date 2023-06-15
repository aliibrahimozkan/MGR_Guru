import numpy as np

class Evaluation:
    def __init__(self):
        pass

    def calculate_pr_at_k(self, model_results:list, sorted_gt_doc_results:list, k: int):
        """
        Calculate Precision@k and Recall@k
        :param model_results: Model Results List
        :param sorted_gt_doc_results: Ground Truth Results List
        :param k: Number of items to consider when computing recall-precision at K
        :return: Precision@k and Recall@k values
        """
        gt_docs = set(sorted_gt_doc_results)
        top_k_recommended = model_results[:k]

        # Count the number of relevant items among the top K
        num_relevant_at_k = len(gt_docs.intersection(top_k_recommended))

        precision_at_k = num_relevant_at_k / k
        recall_at_k = num_relevant_at_k / len(gt_docs) if len(gt_docs) > 0 else 0.0
        return precision_at_k, recall_at_k


    def compute_ndcg_with_ratings(self, model_results:list, sorted_gt_doc_results:list, ratings:list):
        """
        Compute Normalized Discounted Cumulative Gain
        :param model_results: Model Results List
        :param sorted_gt_doc_results: Ground Truth Results List
        :param ratings: TripAdvisor Rating for Ground Truth Results
        :return: Normalized Discounted Cumulative Gain Value [0,1]
        """
        # Compute the Discounted Cumulative Gain (DCG)
        dcg = 0.0
        for i, item in enumerate(model_results):
            if item in sorted_gt_doc_results:
                if i == 0:
                    dcg += ratings[item]
                else:
                    relevance = ratings[item] / np.log2(i + 1)
                    dcg += relevance

        # Compute the Ideal Discounted Cumulative Gain
        idcg = 0.0
        if len(sorted_gt_doc_results)>len(model_results):
            ideal_sorted = sorted_gt_doc_results[:len(model_results)]
        else:
            ideal_sorted = sorted_gt_doc_results[:]
        for i, item in enumerate(ideal_sorted):
            if i == 0:
                idcg += ratings[item]
            else:
                relevance = ratings[item] / np.log2(i + 1)
                idcg += relevance
        ndcg = dcg / idcg if idcg > 0 else 0.0
        return ndcg

    def calculate_average_precision(self, model_results:list, sorted_gt_doc_results:list):
        """
        Calculate Average Precision@k
        :param model_results: recommended restaurants
        :param sorted_gt_doc_results: ground truth restaurants
        :return: avg. precision
        """
        precision_sum = 0.0
        relevant_docs_len_total = len(sorted_gt_doc_results)
        relevant_docs_len_in_results = len(np.intersect1d(model_results, sorted_gt_doc_results))

        if relevant_docs_len_total == 0 or relevant_docs_len_in_results==0:
            return 0.0


        for i, result in enumerate(model_results):
            relevant = int(result in sorted_gt_doc_results)
            precision_k, recall_k = self.calculate_pr_at_k(model_results, sorted_gt_doc_results, i+1)
            precision_sum += (precision_k * relevant)

        average_precision = precision_sum / relevant_docs_len_in_results
        return average_precision

