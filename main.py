import xml.etree.ElementTree as ET
import requests
import pandas as pd
import openpyxl
import os

# Fetch list of 'sido' data (regions), 시도 코드
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
def animal_upr(bgnde, endde, upr_cd):
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
                        'upr_cd': upr_cd,
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

# 군구 코드로 유기동물 조회 확인
def animal_org(bgnde, endde, orgCd):
    url = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic"
    numOfRows = 1000
    pageNo = 1
    all_animal_data = []
    total_count = 0  # Initialize total count for each region

    while True:
        params = {
            'serviceKey': 'eAzNT8F3YVbddScjrLy8w4o2HliaF3Jfk4gAnDSr2O8HGfPqKsrZWgnTgJbR5xzFzc0TSXPXi437ywZqw+zDxw==',
            'bgnde': bgnde,
            'endde': endde,
            'org_cd': orgCd,
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
                # print(f"Fetching page {pageNo}, total records: {total_count} for org_cd: {orgCd}")

            for item in root.findall('.//item'):
                happen_dt = item.findtext('happenDt')
                happen_place = item.findtext('happenPlace')
                if happen_dt and happen_place:
                    all_animal_data.append({
                        'org_cd': orgCd,
                        'happenDt': happen_dt,
                        'happenPlace': happen_place
                    })

            if len(all_animal_data) >= total_count:
                break
            else:
                pageNo += 1
        else:
            print(f"Error: Unable to fetch data for org_cd: {orgCd}. Status code: {response.status_code}")
            break

    return total_count, all_animal_data


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 시 별 유기동물 조회수 분류 확인 - 날짜 조절 가능
def filter_animal_sido(begindate, enddate):
    # ExcelWriter를 사용하여 하나의 파일에 여러 시트를 저장
    with pd.ExcelWriter(f"./광역시_및_도_유기동물_현황_{begindate}~{enddate}.xlsx") as writer:
        for upr_cd, region_name in sigungu_dict.items():
            total_count, animal_data = animal_upr(begindate, enddate, upr_cd)  # Example region and date
            print(f"Total Count for upr_cd {region_name}: {total_count}")
            df = pd.DataFrame.from_dict(animal_data)

            # 시트를 각 region_name에 맞춰서 저장
            df.to_excel(writer, sheet_name=region_name[:31])  # 시트 이름은 31자 제한
            print(df)


# 군구 별 유기동물 조회수 분류 확인 - 날짜 조절 가능
import pandas as pd


def filter_animal_gungu(begindate, enddate):
    # 시도별 최빈 장소와 그 횟수를 저장할 리스트
    frequent_place_data = []
    path = f"./gungu/ {begindate}~{enddate}"
    make_dir(path)

    # 군/구별 유기 동물 수를 기록할 딕셔너리
    gungu_total_counts = {}

    for upr_cd, sido_name in sigungu_dict.items():
        # ExcelWriter를 사용하여 각 시도별 하나의 파일에 여러 시트를 저장
        with pd.ExcelWriter(f"./{path}/{sido_name}_유기동물_현황_{begindate}~{enddate}.xlsx") as writer:
            # 해당 시도에 속한 군/구 목록 가져오기
            if upr_cd in gungu_codes:
                for org_cd, gungu_name in gungu_codes[upr_cd].items():
                    total_count, animal_data = animal_org(begindate, enddate, org_cd)
                    print(f"Total Count for org_cd {gungu_name}: {total_count}")

                    # 군/구별 총 유기 동물 수 기록
                    if total_count > 0:
                        gungu_total_counts[gungu_name] = total_count

                    if animal_data:  # 데이터가 존재하는 경우만 처리
                        df = pd.DataFrame.from_dict(animal_data)

                        # happenPlace의 빈도수 계산
                        place_counts = df['happenPlace'].value_counts()

                        # 가장 많이 유기된 장소를 찾고 저장
                        if not place_counts.empty:
                            most_frequent_place = place_counts.idxmax()  # 가장 많이 유기된 장소
                            most_frequent_count = place_counts.max()  # 유기 횟수

                            # 시/도, 군/구, 최빈 장소, 유기 횟수를 리스트에 저장
                            frequent_place_data.append(
                                [sido_name, gungu_name, most_frequent_place, most_frequent_count])

                        # 시트 이름은 31자 제한, 군/구 이름을 사용
                        sheet_name = gungu_name[:31]

                        # 원래 데이터와 빈도수를 함께 쓰기
                        startrow = len(df) + 2  # 원래 데이터의 끝에서 2줄 아래에 빈도수 기록
                        df.to_excel(writer, sheet_name=sheet_name)

                        # 빈도수 데이터를 시트에 기록
                        place_counts_df = place_counts.reset_index()
                        place_counts_df.columns = ['happenPlace', 'Count']  # 컬럼 이름 지정
                        place_counts_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=startrow)
                        print(f"Saved data for {gungu_name} in {sido_name} file.")
                    else:
                        print(f"No data found for {gungu_name}.")
            else:
                print(f"No gungu data found for {sido_name}.")

    # 최빈 장소 데이터를 데이터프레임으로 변환
    frequent_place_df = pd.DataFrame(frequent_place_data, columns=['Sido', 'Gungu', 'Most Frequent Place', 'Count'])

    # 최빈 장소 데이터프레임을 엑셀로 저장
    frequent_place_df.to_excel(f"./유기동물_최빈장소_{begindate}~{enddate}.xlsx", index=False)
    print(f"Saved most frequent places to 유기동물_최빈장소_{begindate}~{enddate}.xlsx")

    # 군/구별 총 유기 동물 수를 기준으로 상위 10개 군/구 선택
    top_10_gungu = sorted(gungu_total_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # 상위 10개 군/구와 그 유기 동물 수 출력
    print("\nTop 10 군/구 with the highest number of abandonments:")
    for gungu, count in top_10_gungu:
        print(f"{gungu}: {count} times")


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
# 각 시도에 대해 군/구 데이터 수집
for upr_cd, sido_name in sigungu_dict.items():
    sigungu_data = sigungu(upr_cd)  # 각 시도의 군/구 목록을 가져오는 함수
    if sigungu_data:
        gungu_codes[upr_cd] = sigungu_data  # 시도 코드별로 군/구 데이터를 저장



filter_animal_gungu('20230101','20230109')
