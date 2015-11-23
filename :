## Settings
Pry.config.color = true
Pry.config.editor = "vim"

Pry.config.prompt = proc do |obj, level, _|
  prompt = ""
  prompt << "#{Rails.version}@" if defined?(Rails)
  prompt << "#{RUBY_VERSION}"
  "#{prompt} (#{obj})> "
end

## Alias
Pry.config.commands.alias_command "lM", "ls -M"
# Ever get lost in pryland? try w!
Pry.config.commands.alias_command 'w', 'whereami'
# Clear Screen
Pry.config.commands.alias_command '.clr', '.clear'
# binding.pry
Pry.config.commands.alias_command 'c', 'continue'
Pry.config.commands.alias_command 's', 'step'
Pry.config.commands.alias_command 'n', 'next'

# awesome_print
begin
  require "awesome_print"
  AwesomePrint.pry!
rescue LoadError => e
  puts "no awesome_print"
end
