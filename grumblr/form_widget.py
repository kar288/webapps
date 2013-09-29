from django.forms import widgets



class GrumblrInput(widgets.Input):
    error = ''

    # def __init__(self, attrs=None):
    #     self.error = ''
    #     super(GrumblrInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if self.error:
            final_attrs['data-toggle'] = 'popover'
            final_attrs['data-placement'] = 'right'
            final_attrs['data-content'] = self.error
        return super(GrumblrInput, self).render(name, value, final_attrs)


class GrumblrTextInput(GrumblrInput):
    input_type = 'text'

    def __init__(self, attrs=None):
        if attrs is not None:
            self.input_type = attrs.pop('type', self.input_type)
        super(GrumblrTextInput, self).__init__(attrs)


class GrumblrNumberInput(GrumblrTextInput):
    input_type = 'number'


class GrumblrEmailInput(GrumblrTextInput):
    input_type = 'email'


class GrumblrURLInput(GrumblrTextInput):
    input_type = 'url'


class GrumblrPasswordInput(GrumblrTextInput):
    input_type = 'password'

    def __init__(self, attrs=None, render_value=False):
        super(GrumblrPasswordInput, self).__init__(attrs)
        self.render_value = render_value

    def render(self, name, value, attrs=None):
        if not self.render_value: value=None
        return super(GrumblrPasswordInput, self).render(name, value, attrs)

class GrumblrHiddenInput(GrumblrInput):
    input_type = 'hidden'
    is_hidden = True