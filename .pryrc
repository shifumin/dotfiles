## Settings
Pry.config.color = true
Pry.config.editor = 'nvim'

Pry.config.prompt = proc do |obj, level, _|
  prompt = ""
  prompt << "#{Rails.version}@" if defined?(Rails)
  prompt << "#{RUBY_VERSION}"
  "#{prompt} (#{obj})> "
end

# Alias
Pry.commands.alias_command "lM", "ls -M"
Pry.commands.alias_command 'w', 'whereami'
Pry.commands.alias_command '.clr', '.clear'

## pry-byebug
# Hit Enter to repeat last command
Pry::Commands.command /^$/, "repeat last command" do
  _pry_.run_command Pry.history.to_a.last
end

if defined? PryByebug
  Pry.commands.alias_command 'c', 'continue'
  Pry.commands.alias_command 's', 'step'
  Pry.commands.alias_command 'n', 'next'
  Pry.commands.alias_command 'f', 'finish'
end

## pry-stack_explorer
if defined? PryStackExplorer
  Pry.commands.alias_command 'bt', 'show-stack'
  Pry.commands.alias_command 'fr', 'frame'
end

## awesome_print
if defined? AwesomePrint
  begin
    require 'awesome_print'
    Pry.config.print = proc { |output, value| output.puts value.ai }
  rescue LoadError => err
    puts "no awesome_print :("
    puts err
  end
end

## Hirb
if defined? Hirb
  # Slightly dirty hack to fully support in-session Hirb.disable/enable toggling
  Hirb::View.instance_eval do
    def enable_output_method
      @output_method = true
      @old_print = Pry.config.print
      Pry.config.print = proc do |*args|
        Hirb::View.view_or_page_output(args[1]) || @old_print.call(*args)
      end
    end

    def disable_output_method
      Pry.config.print = @old_print
      @output_method = nil
    end
  end

  Hirb.enable
end
