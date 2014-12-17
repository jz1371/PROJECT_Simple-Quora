SimpleQuora
===========
Name:
    Jinxgin Zhu
    jz1371
    N17742161

Webpage:
      http://quora-jz1371.appspot.com/
      
Github Repository:
    https://github.com/jz1371/PROJECT_Simple-Quora

Bonus:

1. Support admin user to delete questions and answers

2. Support emailing updates

3. Keep track of views of questions

4. Order question by combination of number of views and time last modified

Design:

1. Datastore: 
    Model: Question # parent=User.user_id
    Model: Answer # parent=Question.key
    Model: Vote   # parent=Question.key or parent=Answer.key
    Model: Tag
    Model: Image
    
2. Implementation:
    main.py contains all handlers
    
3. Frontend:
    html templates are includes in /templates 

