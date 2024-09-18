import requests
from bs4 import BeautifulSoup


def scrape_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all text content
    texts = soup.get_text(separator=' ')
    return texts


def scrape_seo_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    seo_data = {}

    # Extract title
    title_tag = soup.find('title')
    seo_data['title'] = title_tag.string if title_tag else None

    # Extract meta description
    description_tag = soup.find('meta', attrs={'name': 'description'})
    seo_data['description'] = description_tag['content'] if description_tag else None

    # Extract meta keywords
    keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
    seo_data['keywords'] = keywords_tag['content'] if keywords_tag else None

    # Extract canonical link
    canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
    seo_data['canonical'] = canonical_tag['href'] if canonical_tag else None

    # Extract Open Graph tags
    og_title = soup.find('meta', property='og:title')
    seo_data['og_title'] = og_title['content'] if og_title else None

    og_description = soup.find('meta', property='og:description')
    seo_data['og_description'] = og_description['content'] if og_description else None

    og_image = soup.find('meta', property='og:image')
    seo_data['og_image'] = og_image['content'] if og_image else None

    return seo_data


def scrape_headings(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    headings = {
        'h1': [h1.get_text() for h1 in soup.find_all('h1')],
        'h2': [h2.get_text() for h2 in soup.find_all('h2')],
        'h3': [h3.get_text() for h3 in soup.find_all('h3')],
        'h4': [h4.get_text() for h4 in soup.find_all('h4')],
        'h5': [h5.get_text() for h5 in soup.find_all('h5')],
        'h6': [h6.get_text() for h6 in soup.find_all('h6')]
    }

    return headings


def scrape_image_alts(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract alt attributes from images
    images = []
    for img in soup.find_all('img'):
        alt_text = img.get('alt')
        img_url = img.get('src')
        images.append({
            'url': img_url,
            'alt': alt_text
        })

    return images


def scrape_structured_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract structured data in JSON-LD format
    structured_data = []
    for script in soup.find_all('script', type='application/ld+json'):
        structured_data.append(script.string)

    return structured_data


def scrape_full_seo_data(url):
    seo_data = scrape_seo_data(url)
    text_content = scrape_text(url)
    headings = scrape_headings(url)
    image_alts = scrape_image_alts(url)
    structured_data = scrape_structured_data(url)

    return {
        'seo_data': seo_data,
        'text_content': text_content,
        'headings': headings,
        'image_alts': image_alts,
        'structured_data': structured_data
    }
