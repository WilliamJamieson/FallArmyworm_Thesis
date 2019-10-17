import source.hint    as hint
import source.keyword as keyword


def dom(homo_s:    float,
        homo_r:    float,
        dominance: float) -> hint.variable:
    """
    Calculate the heterozyous parameter using degree of dominance
        SR = (SS + RR)/2 + D*(SS - RR)/2

        SR = heterozyous
        SS = susceptible
        RR = resistant
        D  = degree of dominance

    Args:
        homo_s:    susceptible parameter
        homo_r:    resistant   parameter
        dominance: the dominance

    Returns:
        heterozygous parameter
    """

    avg = (homo_s + homo_r)/2
    sub = (homo_s - homo_r)/2

    hetero = avg + (dominance * sub)

    return {
        keyword.homo_s: homo_s,
        keyword.hetero: hetero,
        keyword.homo_r: homo_r
    }
