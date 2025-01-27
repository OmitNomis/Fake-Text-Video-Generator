from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw
import io
import time

def capture_chat_interface(messages, show_header=True, header_data=None):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--force-device-scale-factor=1')
    chrome_options.add_argument('--window-size=414,900')
    chrome_options.add_argument('--no-sandbox')  # Add this line
    chrome_options.add_argument('--disable-dev-shm-usage')  # Add this line
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get('http://127.0.0.1:5001')
        
        # Wait for the container to be ready
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dynamic-container"))
        )
        
        # Clear any existing messages
        driver.execute_script("document.querySelector('.dynamic-container').innerHTML = '';")
        
        # Update header if provided
        if header_data:
            driver.execute_script("""
                const profileImage = arguments[0];
                const headerName = arguments[1];
                
                if (profileImage) {
                    document.getElementById('profileImage').src = profileImage;
                }
                if (headerName) {
                    document.getElementById('headerName').textContent = headerName;
                }
            """, header_data.get('profileImage', ''), header_data.get('headerName', 'John Doe'))
        
        # Set transparent background
        driver.execute_script("""
            document.body.style.background = 'transparent';
            document.documentElement.style.background = 'transparent';
        """)
        
        # Add messages
        for msg in messages:
            if msg and msg.get('text') and msg['text'].strip():
                driver.execute_script("""
                    const msg = arguments[0];
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${msg.is_sender ? 'sender' : 'receiver'}`;
                    messageDiv.textContent = msg.text.trim();
                    messageDiv.setAttribute('data-id', msg.id);
                    
                    if (msg.soundEffect) {
                        messageDiv.setAttribute('data-sound-effect', msg.soundEffect);
                    }
                    
                    document.querySelector('.dynamic-container').appendChild(messageDiv);
                """, msg)
        
        # Wait for messages to be rendered
        time.sleep(0.5)
        
        # Hide input area and adjust container
        driver.execute_script("""
            const inputArea = document.querySelector('.input-area');
            if (inputArea) inputArea.remove();
            
            const container = document.querySelector('.container');
            const messageContainer = document.getElementById('messageContainer');
            const header = document.querySelector('.header');
            
            if (header) {
                header.style.display = arguments[0] ? 'flex' : 'none';
            }
            
            container.style.minHeight = 'unset';
            container.style.height = 'auto';
            messageContainer.style.height = 'auto';
            messageContainer.style.maxHeight = 'none';
            messageContainer.style.minHeight = 'unset';
        """, show_header)
        
        # Wait for layout to stabilize
        time.sleep(0.5)
        
        # Take screenshot
        container = driver.find_element(By.CLASS_NAME, "container")
        screenshot = container.screenshot_as_png
        
        if not screenshot:
            raise Exception("Failed to capture screenshot")
            
        image = Image.open(io.BytesIO(screenshot))
        
        if not image:
            raise Exception("Failed to process screenshot")
        
        image = image.convert('RGBA')
        
        # Create rounded corners
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (image.size[0]-1, image.size[1]-1)], 20, fill=255)
        
        output = Image.new('RGBA', image.size, (0, 0, 0, 0))
        output.paste(image, mask=mask)
        
        bbox = output.getbbox()
        if bbox:
            output = output.crop(bbox)
        
        return output
        
    except Exception as e:
        print(f"Error capturing chat interface: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        try:
            driver.quit()
        except:
            pass
