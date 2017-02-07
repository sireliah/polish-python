z turtle zaimportuj *
color('red', 'yellow')
begin_fill()
dopóki Prawda:
    forward(200)
    left(170)
    jeżeli abs(pos()) < 1:
        przerwij
end_fill()
done()
