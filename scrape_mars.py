# Import Dependencies
from bs4 import BeautifulSoup
import requests
import pandas as pd
from splinter import Browser 
import time
from flask import Flask, jsonify, render_template
import pymongo

def init_browser():
    # splinter
    executable_path = {'executable_path': 'chromedriver/chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()
    mars_collection = {}
    # NASA.gov Mars Site
    # URL of page to be scraped
    base_url = 'https://mars.nasa.gov'
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'

    # Retrieve page with the requests module
    browser.visit(url)
    # Allow splinter to catch up
    time.sleep(2)
    # Store HTML document
    html = browser.html
    # Create BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')

    # Retrieve the parent divs for all articles
    results = soup.find_all('div', class_='slide')
    
    nasa_news_title = []
    nasa_news_p = []
    counter = 0

    for result in results:
        # scrape the article header 
        headline = result.find('div', class_='content_title').text
        nasa_news_title.append(headline)
        link = base_url + str(result.find('a')['href'])
        description = result.find('div', class_='rollover_description_inner').text
        nasa_news_p.append(description)
        counter += 1
    
    mars_collection["news_title"] = nasa_news_title
    mars_collection["news_description"] = nasa_news_p

    # JPL Mars Space Images Site
    # URL of page to be scraped
    base_url = 'https://www.jpl.nasa.gov'
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    # Retrieve page with splinter
    browser.visit(url)
    # Allow splinter to catch up
    time.sleep(2)
    # Store HTML document
    html = browser.html
    # Create BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')
    
    # click the full image button
    browser.find_by_id('full_image').click()
    # Allow splinter to catch up to updated html after popup appears
    time.sleep(2)    

    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    # find more info button
    more_info_button = soup.find('div', class_='buttons').find_all('a')[1].text

    # click the more info button to go to the largest size image
    browser.find_by_text(more_info_button).click()
    # Allow splinter to catch up
    time.sleep(2)

    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    main_image = soup.find_all('img', class_='main_image')

    # store the main image url
    featured_img_url = str(base_url + main_image[0]['src'])
    mars_collection["featured_image_url"] = featured_img_url

    # Mars Facts Site
    # URL of site to be scraped
    url = 'https://space-facts.com/mars/'

    # Retrieve page with splinter
    browser.visit(url)

    # Use pandas to read for tables
    tables = pd.read_html(url)
    planet_comp_df = tables[1]
    
    # Remove ':' from index column
    clean_index = []

    for row in planet_comp_df.iloc[:,0]:
        new_row_name = row.replace(':', '')
        clean_index.append(new_row_name)

    # Add clean index to df
    planet_comp_df['Key Facts'] = clean_index

    # Reset index to clean index and drop old index
    planet_comp_df = planet_comp_df.set_index('Key Facts')
    planet_comp_df = planet_comp_df.drop(['Mars - Earth Comparison'], axis=1)

    # Convert Table to HTML and store in collection
    planet_comp_df = planet_comp_df.to_html()
    planet_comp_df = planet_comp_df.replace("\n", "")
    mars_collection["mars_facts"] = planet_comp_df

    # Mars Hemispheres Site
    # URL of site to be scraped
    base_url = 'https://astrogeology.usgs.gov/'
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url)

    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    # find html for looping through hemisphere links 
    hemi_pages = soup.find('div', class_='collapsible results').find_all('div', class_='description')
    hemi_pages

    # Setup dictionary for Hemisphere titles and image links
    hemisphere_image_urls = []
    counter = 0

    # Write loop to extract all hemisphere names and image links
    for hemi_page in hemi_pages:
        # create dictionary level for each planet
        hemi_dictionary = {}
        hemi_dictionary['title'] = ''
        hemi_dictionary['img_url'] = ''
    
        # first add title to dictionary
        title = hemi_page.find('h3').text
        title = title.replace(' Enhanced', '')
        hemi_dictionary['title'] = title
        hemisphere_image_urls.append(hemi_dictionary)
    
        # next add the image url
        hemi_page_url = base_url + hemi_pages[counter].find('a')['href']
        # visit the hemisphere page
        browser.visit(hemi_page_url)
        # Allow Splinter to catch up to updated html
        time.sleep(5)
    
        # retrieve new html
        # HTML object
        html = browser.html
        # Parse HTML with Beautiful Soup
        soup = BeautifulSoup(html, 'html.parser')
        # Find the text on the jpg download link
        img_url = str(soup.find('div', class_='downloads').find('li').find('a')['href'])

        # increase the counter and add the dictionary to the hemisphere list
        counter += 1
        hemi_dictionary['img_url'] = img_url
    
    mars_collection["hemisphere_images"] = hemisphere_image_urls
    browser.quit()
    return mars_collection