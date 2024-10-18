import xml.etree.ElementTree as ET
import requests

# Fetch list of 'sido' data (regions)
def sido(numOfRows, pageNo):
    url = 'http://apis.data.go.kr/1543061/abandonmentPublicSrvc/sido'
    params = {
        'serviceKey': 'eAzNT8F3YVbddScjrLy8w4o2HliaF3Jfk4gAnDSr2O8HGfPqKsrZWgnTgJbR5xzFzc0TSXPXi437ywZqw+zDxw==',
        'numOfRows': numOfRows,
        'pageNo': pageNo,
        '_type': 'xml'  # Ensure XML response
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        sido_dict = {}
        for item in root.findall('.//item'):
            org_cd = item.findtext('orgCd')
            orgdown_nm = item.findtext('orgdownNm')
            if org_cd and orgdown_nm:
                sido_dict[org_cd] = orgdown_nm
        return sido_dict
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None

# Fetch list of 'sigungu' data (cities under regions)
def sigungu(upr_cd):
    url = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/sigungu"
    params = {'serviceKey': 'eAzNT8F3YVbddScjrLy8w4o2HliaF3Jfk4gAnDSr2O8HGfPqKsrZWgnTgJbR5xzFzc0TSXPXi437ywZqw+zDxw==', 'upr_cd': upr_cd }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        sigungu_dict = {}
        for item in root.findall('.//item'):
            org_cd = item.findtext('orgCd')
            orgdown_nm = item.findtext('orgdownNm')
            if org_cd and orgdown_nm:
                sigungu_dict[org_cd] = orgdown_nm
        return sigungu_dict
    else:
        print(f"Error: Unable to fetch data for upr_cd: {upr_cd}. Status code: {response.status_code}")
        return None

# Fetch animal data based on region and date, returning totalCount
def animal(bgnde, endde, upr_cd):
    url = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic"
    numOfRows = 500  
    pageNo = 1
    all_animal_data = []
    total_count = 0  # Initialize total count for each region

    while True:
        params = {
            'serviceKey': 'eAzNT8F3YVbddScjrLy8w4o2HliaF3Jfk4gAnDSr2O8HGfPqKsrZWgnTgJbR5xzFzc0TSXPXi437ywZqw+zDxw==',
            'bgnde': bgnde,
            'endde': endde,
            'upr_cd': upr_cd,
            'pageNo': pageNo,
            'numOfRows': numOfRows,
            '_type': 'xml'
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            # Fetch total count on the first page only
            if pageNo == 1:
                total_count = int(root.findtext('.//totalCount'))
                print(f"Fetching page {pageNo}, total records: {total_count} for upr_cd: {upr_cd}")

            for item in root.findall('.//item'):
                happen_dt = item.findtext('happenDt')
                happen_place = item.findtext('happenPlace')
                if happen_dt and happen_place:
                    all_animal_data.append({
                        'happenDt': happen_dt,
                        'happenPlace': happen_place
                    })

            if len(all_animal_data) >= total_count:
                break
            else:
                pageNo += 1  
        else:
            print(f"Error: Unable to fetch data for upr_cd: {upr_cd}. Status code: {response.status_code}")
            break

    return total_count, all_animal_data



# Main process: fetching data and calculating region counts
sigungu_dict = {
    '6110000': '서울특별시', '6260000': '부산광역시', '6270000': '대구광역시',
    '6280000': '인천광역시', '6290000': '광주광역시', '5690000': '세종특별자치시',
    '6300000': '대전광역시', '6310000': '울산광역시', '6410000': '경기도',
    '6530000': '강원특별자치도', '6430000': '충청북도', '6440000': '충청남도',
    '6540000': '전북특별자치도', '6460000': '전라남도', '6470000': '경상북도',
    '6480000': '경상남도', '6500000': '제주특별자치도'
}

# Fetching sigungu data for each sido
gungu_codes = {}
for upr_cd in sigungu_dict.keys():
    sigungu_data = sigungu(upr_cd)
    if sigungu_data:
        gungu_codes.update(sigungu_data)

# Example: Fetching animal data and totalCount for each upr_cd
for upr_cd in sigungu_dict.keys():
    total_count, animal_data = animal('20230101', '20230131', upr_cd)  # Example region and date
    print(f"Total Count for upr_cd {upr_cd}: {total_count}")
    # print(animal_data)
