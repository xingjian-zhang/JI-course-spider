chromedriver_path = 'chromedriver.exe'
select_course_url = 'http://coursesel.umji.sjtu.edu.cn/welcome.action'
api_key = '129eea671c88957'
user_name = ''
pass_word = ''
x_path = {
    'captcha': '//*[@id="captcha-img"]',
    'turn': '//*[@id="electTurn"]/div[1]/div[1]/div[1]/a',
    'preview': '/html/body/div[2]/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div[4]',
    'username_input':'//*[@id="user"]',
    'password_input':'//*[@id="pass"]',
    'captcha_input':'//*[@id="captcha"]',
    'login': '//*[@id="submit-button"]',
    'refresh': '/html/body/div[2]/div[1]/div/div[2]/div[3]/div/div[1]/div/div[2]/div/ul/li[4]/div'
}
