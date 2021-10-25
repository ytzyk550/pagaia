import webbrowser


def calculate_m_slope(x1, x2, y1, y2):
    # calculate line slope equation
    m = (float(y2)-float(y1))/(float(x2)-float(x1))
    return m


def calculate_point_sum(x, m, b):
    # calculate linear equation
    return (m*x) + b


def open_url_on_chrome(url: str):

    webbrowser.register('chrome',
                        None,
                        webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
    webbrowser.get('chrome').open_new(url)
