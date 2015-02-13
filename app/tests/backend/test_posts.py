'''
Created on Feb 11, 2015

@author: Jingxin Zhu 
'''

# from ferris.tests.lib import WithTestBed
from app.models.post import Post
from ferrisnose import FerrisAppTest


class TestPost(FerrisAppTest):

    def testQueries(self):
        # log in user one
        self.loginUser('user1@example.com')

        # create two posts
        post1 = Post(title="Post 1")
        post1.put()
        post2 = Post(title="Post 2")
        post2.put()

        # log in user two
        self.loginUser('user2@example.com')

        # create two more posts
        post3 = Post(title="Post 3")
        post3.put()
        post4 = Post(title="Post 4")
        post4.put()

        # Get all posts
        all_posts = list(Post.all_posts())

        # Make sure there are 4 posts in total
        assert len(all_posts) == 4 

        # Make sure they're in the right order
        assert all_posts == [post4, post3, post2, post1]

        # Make sure we only get two for user2, and that they're the right posts
        user2_posts = list(Post.all_posts_by_user())

        assert len(user2_posts) == 2
        assert user2_posts == [post4, post3]

        # Test all posts shown up
        resp = self.testapp.get('/posts')
        assert 'Post 1' in resp.body
        assert 'Post 2' in resp.body
        assert 'Post 3' in resp.body
        assert 'Post 4' in resp.body
         
        # Test posts_created_by_user
        resp = self.testapp.get('/posts?=mine')
        assert 'Post 1' not in resp.body
        assert 'Post 2' not in resp.body
        assert 'Post 3' in resp.body
        assert 'Post 4' in resp.body
         
        # Test 'edit' link exists
        assert 'Edit' in resp.body
         
    def testAdd(self):
        self.loginUser("user1@example.com")
        resp = self.testapp.get('/posts/add')
         
        # Test not filling requried will cause validation error
        form = resp.form
        error_resp = form.submit()
        assert 'This field is required' in error_resp.body
         
        # Test add successfully
        form['title'] = 'Test Post'
        good_resp = form.submit()
        assert good_resp.status_int == 302  # Success redirects us to list
         
        # Load new page and verify Post
        final_resp = good_resp.follow()
        assert 'Test Post' in final_resp
