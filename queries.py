import mysql.connector

############################ Games ##############################
def q_game_rating(cursorObject, platform, top_n):
    query = """
        SELECT G.Name, AVG(PPGP.Rating) as Rating
        FROM Games as G
        INNER JOIN Player_Platform_Games_Play as PPGP on G.GameID = PPGP.GameID
        INNER JOIN Platform as P on PPGP.PlatformID = P.PlatformID
        WHERE P.PlatformName = %s
        GROUP BY G.GameID
        ORDER BY Rating DESC
        LIMIT %s
    """
    cursorObject.execute(query, (platform, top_n))
    return cursorObject.fetchall()


def q_game_genre(cursorObject, genre, order_attri, order="DESC"):
    if order.upper() not in ["ASC", "DESC"]:
        raise ValueError("Invalid sort order")
    query = f"""
        SELECT GameID, Name, {order_attri}
        FROM Games
        WHERE Genre = %s
        ORDER BY {order_attri} {order}
    """
    cursorObject.execute(query, (genre,))
    return cursorObject.fetchall()


def q_game_pub_dev(cursorObject, publisher=None, developer=None):
    if publisher:
        query = """
            SELECT G.GameID, G.ReleaseDate
            FROM Games as G
            INNER JOIN Publisher_Games as PG on G.GameID = PG.GameID
            INNER JOIN Publisher as P on PG.PublisherID = P.PublisherID
            WHERE P.PublisherName = %s
            ORDER BY G.ReleaseDate ASC
        """
        cursorObject.execute(query, (publisher,))
    elif developer:
        query = """
            SELECT G.GameID, G.ReleaseDate
            FROM Games as G
            INNER JOIN Developer_Games as DG on G.GameID = DG.GameID
            INNER JOIN Developer as D on DG.DeveloperID = D.DeveloperID
            WHERE D.DeveloperName = %s
            ORDER BY G.ReleaseDate ASC
        """
        cursorObject.execute(query, (developer,))
    else:
        return []
    return cursorObject.fetchall()


def q_game_year(cursorObject, year):
    query = """
        SELECT G.Name, G.ReleaseDate, PF.PlatformName, D.DeveloperName, P.PublisherName
        FROM Games as G
        INNER JOIN Platform_Support_Games as PSG on G.GameID = PSG.GameID
        INNER JOIN Platform as PF on PSG.PlatformID = PF.PlatformID
        INNER JOIN Developer_Games as DG on G.GameID = DG.GameID
        INNER JOIN Developer as D on DG.DeveloperID = D.DeveloperID
        INNER JOIN Publisher_Games as PG on G.GameID = PG.GameID
        INNER JOIN Publisher as P on PG.PublisherID = P.PublisherID
        WHERE G.ReleaseDate >= %s
        ORDER BY G.ReleaseDate ASC
    """
    cursorObject.execute(query, (f"{year}-01-01",))
    return cursorObject.fetchall()


def q_genre_avg_rating(cursorObject, type=None):
    if type == "Rating":
        query = """
            SELECT G.Genre, AVG(PPGP.Rating) AS AverageRating
            FROM Games AS G
            INNER JOIN Player_Platform_Games_Play AS PPGP ON G.GameID = PPGP.GameID
            WHERE G.Genre IS NOT NULL
            GROUP BY G.Genre
            ORDER BY AverageRating DESC
        """
    elif type == "UnitsSold":
        query = """
            SELECT Genre, SUM(UnitsSold) AS TotalUnitsSold
            FROM Games
            WHERE Genre IS NOT NULL
            GROUP BY Genre
            ORDER BY TotalUnitsSold DESC
        """
    else:
        return []
    
    cursorObject.execute(query)
    return cursorObject.fetchall()


############################ Users ##############################
def q_user_achievements_by_game(cursorObject, game_id, top_n):
    query = '''
        SELECT PlayerID, COUNT(*) AS AchievementsUnlocked
        FROM Player_Unlock_Achievement
        WHERE GameID = %s
        GROUP BY PlayerID
        ORDER BY AchievementsUnlocked DESC
        LIMIT %s;
    '''
    cursorObject.execute(query, (game_id, top_n))
    return cursorObject.fetchall()


def q_user_top_playtime_by_game(cursorObject, game_id, top_n):
    query = '''
        SELECT P.UserName, SUM(PPGP.TotalPlayingTime) AS TotalTime
        FROM Player_Platform_Games_Play PPGP
        JOIN Player P ON PPGP.PlayerID = P.UserID
        WHERE PPGP.GameID = %s
        GROUP BY P.UserID, P.UserName
        ORDER BY TotalTime DESC
        LIMIT %s;
    '''
    cursorObject.execute(query, (game_id, top_n))
    return cursorObject.fetchall()


def q_user_total_spent(cursorObject, user_id):
    query = '''
        SELECT SUM(PurchasePrice) AS TotalSpent
        FROM Player_Platform_Games_Play
        WHERE PlayerID = %s;
    '''
    cursorObject.execute(query, (user_id,))
    return cursorObject.fetchall()


def q_user_purchases(cursorObject, user_id):
    query = '''
        SELECT G.Name AS GameName, PF.PlatformName, PPGP.PurchasePrice, PPGP.PurchaseTime
        FROM Player_Platform_Games_Play AS PPGP
        JOIN Games G ON G.GameID = PPGP.GameID
        JOIN Platform PF ON PF.PlatformID = PPGP.PlatformID
        WHERE PPGP.PlayerID = %s
        ORDER BY PPGP.PurchaseTime DESC;
    '''
    cursorObject.execute(query, (user_id,))
    return cursorObject.fetchall()


def q_user_friends_by_mutualtime(cursorObject, user_id, min_time):
    query = '''
        SELECT p2.UserID, p2.UserName, p2.Email, p2.Region, pf.MutualTime
        FROM Player_Friends pf
        JOIN Player p2 ON pf.Player2ID = p2.UserID
        WHERE pf.Player1ID = %s AND pf.MutualTime >= %s;
    '''
    cursorObject.execute(query, (user_id, min_time))
    return cursorObject.fetchall()


###################### Developer/ Publisher #####################
def q_dev_pub_revenues(cursorObject, role, start_year, end_year, top_n):
    if role == "Developer":
        query = """
            SELECT D.DeveloperName, SUM(G.UnitsSold * PSG.Price) AS TotalRevenue
            FROM Games G
            INNER JOIN Developer_Games DG ON G.GameID = DG.GameID
            INNER JOIN Developer D ON DG.DeveloperID = D.DeveloperID
            INNER JOIN Platform_Support_Games PSG ON G.GameID = PSG.GameID
            WHERE DG.DevelopeFinishYear BETWEEN %s AND %s
            GROUP BY D.DeveloperID
            ORDER BY TotalRevenue DESC
            LIMIT %s
        """
    elif role == "Publisher":
        query = """
            SELECT P.PublisherName, SUM(G.UnitsSold * PSG.Price) AS TotalRevenue
            FROM Games G
            INNER JOIN Publisher_Games PG ON G.GameID = PG.GameID
            INNER JOIN Publisher P ON PG.PublisherID = P.PublisherID
            INNER JOIN Platform_Support_Games PSG ON G.GameID = PSG.GameID
            WHERE PG.PublishYear BETWEEN %s AND %s
            GROUP BY P.PublisherID
            ORDER BY TotalRevenue DESC
            LIMIT %s
        """
    else:
        return []
    
    cursorObject.execute(query, (start_year, end_year, top_n))
    return cursorObject.fetchall()


def q_dev_pub_rating(cursorObject, role, rating_threshold):
    if role == "Developer":
        query = """
            SELECT D.DeveloperName, COUNT(DISTINCT G.GameID) AS HighRatedGames
            FROM Games G
            INNER JOIN Developer_Games DG ON G.GameID = DG.GameID
            INNER JOIN Developer D ON DG.DeveloperID = D.DeveloperID
            INNER JOIN Player_Platform_Games_Play PPGP ON G.GameID = PPGP.GameID
            WHERE PPGP.Rating > %s
            GROUP BY D.DeveloperID
            ORDER BY HighRatedGames DESC
        """
    elif role == "Publisher":
        query = """
            SELECT P.PublisherName, COUNT(DISTINCT G.GameID) AS HighRatedGames
            FROM Games G
            INNER JOIN Publisher_Games PG ON G.GameID = PG.GameID
            INNER JOIN Publisher P ON PG.PublisherID = P.PublisherID
            INNER JOIN Player_Platform_Games_Play PPGP ON G.GameID = PPGP.GameID
            WHERE PPGP.Rating > %s
            GROUP BY P.PublisherID
            ORDER BY HighRatedGames DESC
        """
    else:
        return []
    
    cursorObject.execute(query, (rating_threshold,))
    return cursorObject.fetchall()


def q_dev_pub_compatibility(cursorObject, role, platform_threshold):
    if role == "Developer":
        query = """
            SELECT D.DeveloperName, COUNT(*) AS GameCount
            FROM (
                SELECT G.GameID, COUNT(DISTINCT PSG.PlatformID) AS PlatformCount
                FROM Games G
                INNER JOIN Platform_Support_Games PSG ON G.GameID = PSG.GameID
                GROUP BY G.GameID
                HAVING PlatformCount > %s
            ) AS CompatibleGames
            INNER JOIN Developer_Games DG ON CompatibleGames.GameID = DG.GameID
            INNER JOIN Developer D ON DG.DeveloperID = D.DeveloperID
            GROUP BY D.DeveloperID
            ORDER BY GameCount DESC
        """
    elif role == "Publisher":
        query = """
            SELECT P.PublisherName, COUNT(*) AS GameCount
            FROM (
                SELECT G.GameID, COUNT(DISTINCT PSG.PlatformID) AS PlatformCount
                FROM Games G
                INNER JOIN Platform_Support_Games PSG ON G.GameID = PSG.GameID
                GROUP BY G.GameID
                HAVING PlatformCount > %s
            ) AS CompatibleGames
            INNER JOIN Publisher_Games PG ON CompatibleGames.GameID = PG.GameID
            INNER JOIN Publisher P ON PG.PublisherID = P.PublisherID
            GROUP BY P.PublisherID
            ORDER BY GameCount DESC
        """
    else:
        return []

    cursorObject.execute(query, (platform_threshold,))
    return cursorObject.fetchall()


########################### Platform ############################
def q_platform_exclusive_games(cursorObject, platform_name): #### Add queries attributes
    sql = """
        SELECT g.Name
        FROM Games g
        JOIN Platform_Support_Games p ON g.GameID = p.GameID
        JOIN Platform pf ON pf.PlatformID = p.PlatformID
        WHERE pf.PlatformName = %s
        AND g.GameID NOT IN (
            SELECT p2.GameID
            FROM Platform_Support_Games p2
            JOIN Platform pf2 ON p2.PlatformID = pf2.PlatformID
            WHERE pf2.PlatformName != %s
        )
        LIMIT 20;
    """
    cursorObject.execute(sql, (platform_name, platform_name))
    return cursorObject.fetchall()


def q_platform_revenue(cursorObject, platform_name, year): #### Add queries attributes
    sql = """
        SELECT SUM(g.UnitsSold * psg.Price) AS EstimatedRevenue
        FROM Platform_Support_Games psg
        JOIN Platform pf ON pf.PlatformID = psg.PlatformID
        JOIN Games g ON psg.GameID = g.GameID
        WHERE pf.PlatformName = %s AND YEAR(psg.IssuedTime) = %s;
    """
    cursorObject.execute(sql, (platform_name, year))
    return cursorObject.fetchone()  # returns (revenue,)


def q_platform_user(cursorObject, platform_name, min_hours): #### Add queries attributes
    sql = """
        SELECT COUNT(*) 
        FROM Player_Use_Platform pup
        JOIN Platform pf ON pf.PlatformID = pup.PlatformID
        WHERE pf.PlatformName = %s AND pup.TotalTimeSpent >= %s;
    """
    cursorObject.execute(sql, (platform_name, min_hours))
    return cursorObject.fetchone()  # returns (count,)