from datetime import date, datetime

def get_grouped_company_data(companynames_and_dates, matched_companies_results):
    # 리스트를 회사 이름(key)을 기준으로 딕셔너리로 변환 (O(1) 조회를 위함)
    company_info_map = {item['companyName']: item for item in companynames_and_dates}

    grouped_company_data = []
    for company_name, company_data in matched_companies_results:
        investment = None
        organization = None
        mae = None

        # 딕셔너리에서 바로 회사 정보 조회
        employment_info = company_info_map.get(company_name)
        start_end_dates = employment_info.get('startEndDates', []) if employment_info else []
        
        if isinstance(company_data, dict):
            mae = company_data.get('mae')
            
            # Investment data processing
            raw_investment = company_data.get('investment')
            investment_found = False
            if raw_investment and raw_investment.get('data') and start_end_dates:
                valid_investments = [inv for inv in raw_investment.get('data', []) if inv.get('announcedAt', {}).get('value')]
                for inv in sorted(valid_investments, key=lambda x: x.get('announcedAt', {}).get('value'), reverse=True):
                    inv_date_str = inv.get('announcedAt', {}).get('value')
                    if not inv_date_str:
                        continue
                    try:
                        inv_date = datetime.fromisoformat(inv_date_str.split('T')[0]).date()
                        for date_range in start_end_dates:
                            start_dict = date_range.get('start')
                            end_dict = date_range.get('end')
                            if not start_dict or not end_dict:
                                continue
                            
                            start = date(start_dict['year'], start_dict['month'], start_dict.get('day', 1))
                            end = date(end_dict['year'], end_dict['month'], end_dict.get('day', 1))

                            if start <= inv_date <= end:
                                investment = {
                                    'level': inv.get('level'),
                                    'totalInvestmentAmount': raw_investment.get('totalInvestmentAmount')
                                }
                                investment_found = True
                                break 
                    except (ValueError, TypeError, KeyError):
                        continue
                    if investment_found:
                        break

            # Organization data processing
            raw_organization = company_data.get('organization')
            organization_found = False
            if raw_organization and raw_organization.get('data') and start_end_dates:
                valid_organizations = [org for org in raw_organization.get('data', []) if org.get('referenceMonth')]
                for org in sorted(valid_organizations, key=lambda x: x.get('referenceMonth'), reverse=True):
                    ref_month_str = org.get('referenceMonth')
                    if not ref_month_str:
                        continue
                    try:
                        year, month = map(int, ref_month_str.split('-'))
                        ref_date = date(year, month, 1)
                        for date_range in start_end_dates:
                            start_dict = date_range.get('start')
                            end_dict = date_range.get('end')
                            if not start_dict or not end_dict:
                                continue

                            start = date(start_dict['year'], start_dict['month'], start_dict.get('day', 1))
                            end = date(end_dict['year'], end_dict['month'], end_dict.get('day', 1))

                            if start <= ref_date <= end:
                                organization = {
                                    'value': org.get('value'),
                                    'growRate': org.get('growRate'),
                                    'referenceMonth': org.get('referenceMonth')
                                }
                                organization_found = True
                                break
                    except (ValueError, TypeError, KeyError):
                        continue
                    if organization_found:
                        break
        
        grouped_company_data.append({
            "name": company_name,
            "mae": mae,
            "investment": investment,
            "organization": organization
        })
    return grouped_company_data
